# pylint:disable=line-too-long

"""
Parser for ssh public keys. Currently supports ssh-rsa, ssh-dsa, ssh-ed25519 and ssh-dss keys.

import sys


key_data = open("ssh-pubkey-file.pem").read()
ssh_key = SSHKey(key_data)
try:
    ssh_key.parse()
except InvalidKeyException:
    print("Invalid key")
    sys.exit(1)
print(ssh_key.bits)

"""

import base64
import binascii
import hashlib
import re
import struct
import sys
import warnings
import ecdsa

from Crypto.PublicKey import RSA, DSA

from .exceptions import *  # pylint:disable=wildcard-import

__all__ = ["SSHKey"]


class SSHKey(object):  # pylint:disable=too-many-instance-attributes
    """
    ssh_key = SSHKey(key_data, strict=True)
    ssh_key.parse()

    strict=True (default) only allows keys ssh-keygen generates. Setting strict mode to false allows
    all keys OpenSSH actually accepts, including highly insecure ones. For example, OpenSSH accepts
    512-bit DSA keys and 64-bit RSA keys which are highly insecure.
    """

    DSA_MIN_LENGTH_STRICT = 1024
    DSA_MAX_LENGTH_STRICT = 1024
    DSA_MIN_LENGTH_LOOSE = 1
    DSA_MAX_LENGTH_LOOSE = 16384

    DSA_N_LENGTH = 160

    ECDSA_CURVE_DATA = {
        b"nistp256": (ecdsa.curves.NIST256p, hashlib.sha256),
        b"nistp192": (ecdsa.curves.NIST192p, hashlib.sha256),
        b"nistp224": (ecdsa.curves.NIST224p, hashlib.sha256),
        b"nistp384": (ecdsa.curves.NIST384p, hashlib.sha384),
        b"nistp521": (ecdsa.curves.NIST521p, hashlib.sha512),
    }

    RSA_MIN_LENGTH_STRICT = 1024
    RSA_MAX_LENGTH_STRICT = 16384
    RSA_MIN_LENGTH_LOOSE = 768
    RSA_MAX_LENGTH_LOOSE = 16384

    # Valid as of OpenSSH_6.9p1
    # argument name, value is mandatory. Options are case-insensitive, but this list must be in lowercase.
    OPTIONS_SPEC = [
        ("agent-forwarding", False),
        ("cert-authority", False),
        ("command", True),
        ("environment", True),
        ("from", True),
        ("no-agent-forwarding", False),
        ("no-port-forwarding", False),
        ("no-pty", False),
        ("no-user-rc", False),
        ("no-x11-forwarding", False),
        ("permitopen", True),
        ("port-forwarding", False),
        ("principals", True),
        ("pty", False),
        ("restrict", False),
        ("tunnel", True),
        ("user-rc", False),
        ("x11-forwarding", False),
    ]
    OPTION_NAME_RE = re.compile("^[A-Za-z0-9-]+$")

    INT_LEN = 4

    FIELDS = ["rsa", "dsa", "ecdsa", "bits", "comment", "options", "options_raw", "key_type"]

    def __init__(self, keydata=None, **kwargs):
        self.keydata = keydata
        self._decoded_key = None
        self.rsa = None
        self.dsa = None
        self.ecdsa = None
        self.bits = None
        self.comment = None
        self.options = None
        self.options_raw = None
        self.key_type = None
        self.strict_mode = bool(kwargs.get("strict", True))
        self.skip_option_parsing = bool(kwargs.get("skip_option_parsing", False))
        if keydata:
            try:
                self.parse(keydata)
            except (InvalidKeyException, NotImplementedError):
                pass

    def reset(self):
        """ Reset all data fields """
        for field in self.FIELDS:
            setattr(self, field, None)

    def hash(self):
        """ Calculate md5 fingerprint.

        Deprecated, use .hash_md5() instead.
        """
        warnings.warn("hash() is deprecated. Use hash_md5(), hash_sha256() or hash_sha512() instead.")
        return self.hash_md5().replace(b"MD5:", b"")

    def hash_md5(self):
        """ Calculate md5 fingerprint.

        Shamelessly copied from http://stackoverflow.com/questions/6682815/deriving-an-ssh-fingerprint-from-a-public-key-in-python

        For specification, see RFC4716, section 4.
        """
        fp_plain = hashlib.md5(self._decoded_key).hexdigest()
        return "MD5:" + ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))

    def hash_sha256(self):
        """ Calculate sha256 fingerprint. """
        fp_plain = hashlib.sha256(self._decoded_key).digest()
        return (b"SHA256:" + base64.b64encode(fp_plain).replace(b"=", b"")).decode("utf-8")

    def hash_sha512(self):
        """ Calculates sha512 fingerprint. """
        fp_plain = hashlib.sha512(self._decoded_key).digest()
        return (b"SHA512:" + base64.b64encode(fp_plain).replace(b"=", b"")).decode("utf-8")

    def _unpack_by_int(self, data, current_position):
        """ Returns a tuple with (location of next data field, contents of requested data field). """
        # Unpack length of data field
        try:
            requested_data_length = struct.unpack('>I', data[current_position:current_position + self.INT_LEN])[0]
        except struct.error:
            raise MalformedDataException("Unable to unpack %s bytes from the data" % self.INT_LEN)

        # Move pointer to the beginning of the data field
        current_position += self.INT_LEN
        remaining_data_length = len(data[current_position:])

        if remaining_data_length < requested_data_length:
            raise MalformedDataException("Requested %s bytes, but only %s bytes available." % (requested_data_length, remaining_data_length))

        next_data = data[current_position:current_position + requested_data_length]
        # Move pointer to the end of the data field
        current_position += requested_data_length
        return current_position, next_data

    @classmethod
    def _parse_long(cls, data):
        """ Calculate two's complement """
        if sys.version < '3':
            ret = long(0)
            for byte in data:
                ret = (ret << 8) + ord(byte)
        else:
            ret = 0  # pylint:disable=redefined-variable-type
            for byte in data:
                ret = (ret << 8) + byte
        return ret

    def _split_key(self, data):
        options_raw = None
        # Terribly inefficient way to remove options, but hey, it works.
        if not data.startswith("ssh-") and not data.startswith("ecdsa-"):
            quote_open = False
            for i, character in enumerate(data):
                if character == '"':  # only double quotes are allowed, no need to care about single quotes
                    quote_open = not quote_open
                if quote_open:
                    continue
                if character == " ":
                    # Data begins after the first space
                    options_raw = data[:i]
                    data = data[i + 1:]
                    break
            else:
                raise MalformedDataException("Couldn't find beginning of the key data")
        key_parts = data.strip().split(None, 2)
        if len(key_parts) < 2:  # Key type and content are mandatory fields.
            raise InvalidKeyException("Unexpected key format: at least type and base64 encoded value is required")
        if len(key_parts) == 3:
            self.comment = key_parts[2]
            key_parts = key_parts[0:2]
        if options_raw:
            # Populate and parse options field.
            self.options_raw = options_raw
            if not self.skip_option_parsing:
                self.options = self.parse_options(self.options_raw)
        else:
            # Set empty defaults for fields
            self.options_raw = None
            self.options = {}
        return key_parts

    @classmethod
    def decode_key(cls, pubkey_content):
        """ Decode base64 coded part of the key. """
        try:
            decoded_key = base64.b64decode(pubkey_content.encode("ascii"))
        except (TypeError, binascii.Error):
            raise MalformedDataException("Unable to decode the key")
        return decoded_key

    @classmethod
    def _bits_in_number(cls, number):
        return len(format(number, "b"))

    def parse_options(self, options):
        """ Parses ssh options string """
        quote_open = False
        parsed_options = {}

        def parse_add_single_option(opt):
            """ Parses and validates a single option, and adds it to parsed_options field. """
            if "=" in opt:
                opt_name, opt_value = opt.split("=", 1)
                opt_value = opt_value.replace('"', '')
            else:
                opt_name = opt
                opt_value = True
            if " " in opt_name or not self.OPTION_NAME_RE.match(opt_name):
                raise InvalidOptionNameException("%s is not valid option name." % opt_name)
            if self.strict_mode:
                for valid_opt_name, value_required in self.OPTIONS_SPEC:
                    if opt_name.lower() == valid_opt_name:
                        if value_required and opt_value is True:
                            raise MissingMandatoryOptionValueException("%s is missing mandatory value." % opt_name)
                        break
                else:
                    raise UnknownOptionNameException("%s is unrecognized option name." % opt_name)
            if opt_name not in parsed_options:
                parsed_options[opt_name] = []
            parsed_options[opt_name].append(opt_value)

        start_of_current_opt = 0
        i = 1  # Need to be set for empty options strings
        for i, character in enumerate(options):
            if character == '"':  # only double quotes are allowed, no need to care about single quotes
                quote_open = not quote_open
            if quote_open:
                continue
            if character == ",":
                opt = options[start_of_current_opt:i]
                parse_add_single_option(opt)
                start_of_current_opt = i + 1
                # Data begins after the first space
        if start_of_current_opt + 1 != i:
            opt = options[start_of_current_opt:]
            parse_add_single_option(opt)
        if quote_open:
            raise InvalidOptionsException("Unbalanced quotes.")
        return parsed_options

    def _process_ssh_rsa(self, data):
        """ Parses ssh-rsa public keys """
        current_position, raw_e = self._unpack_by_int(data, 0)
        current_position, raw_n = self._unpack_by_int(data, current_position)

        unpacked_e = self._parse_long(raw_e)
        unpacked_n = self._parse_long(raw_n)

        self.rsa = RSA.construct((unpacked_n, unpacked_e))
        self.bits = self.rsa.size() + 1

        if self.strict_mode:
            min_length = self.RSA_MIN_LENGTH_STRICT
            max_length = self.RSA_MAX_LENGTH_STRICT
        else:
            min_length = self.RSA_MIN_LENGTH_LOOSE
            max_length = self.RSA_MAX_LENGTH_LOOSE
        if self.bits < min_length:
            raise TooShortKeyException("%s key data can not be shorter than %s bits (was %s)" % (self.key_type, min_length, self.bits))
        if self.bits > max_length:
            raise TooLongKeyException("%s key data can not be longer than %s bits (was %s)" % (self.key_type, max_length, self.bits))
        return current_position

    def _process_ssh_dss(self, data):
        """ Parses ssh-dsa public keys """
        data_fields = {}
        current_position = 0
        for item in ("p", "q", "g", "y"):
            current_position, value = self._unpack_by_int(data, current_position)
            data_fields[item] = self._parse_long(value)

        self.dsa = DSA.construct((data_fields["y"], data_fields["g"], data_fields["p"], data_fields["q"]))
        self.bits = self.dsa.size() + 1

        q_bits = self._bits_in_number(data_fields["q"])
        if q_bits != self.DSA_N_LENGTH:
            raise InvalidKeyException("Incorrect DSA key parameters: bits(p)=%s, q=%s" % (self.bits, q_bits))
        if self.strict_mode:
            min_length = self.DSA_MIN_LENGTH_STRICT
            max_length = self.DSA_MAX_LENGTH_STRICT
        else:
            min_length = self.DSA_MIN_LENGTH_LOOSE
            max_length = self.DSA_MAX_LENGTH_LOOSE
        if self.bits < min_length:
            raise TooShortKeyException("%s key can not be shorter than %s bits (was %s)" % (self.key_type, min_length, self.bits))
        if self.bits > max_length:
            raise TooLongKeyException("%s key data can not be longer than %s bits (was %s)" % (self.key_type, max_length, self.bits))
        return current_position

    def _process_ecdsa_sha(self, data):
        """ Parses ecdsa-sha public keys """
        current_position, curve_information = self._unpack_by_int(data, 0)
        if curve_information not in self.ECDSA_CURVE_DATA:
            raise NotImplementedError("Invalid curve type: %s" % curve_information)
        curve, hash_algorithm = self.ECDSA_CURVE_DATA[curve_information]

        current_position, key_data = self._unpack_by_int(data, current_position)
        try:
            # data starts with \x04, which should be discarded.
            ecdsa_key = ecdsa.VerifyingKey.from_string(key_data[1:], curve, hash_algorithm)
        except AssertionError:
            raise InvalidKeyException("Invalid ecdsa key")
        self.bits = int(curve_information.replace(b"nistp", b""))
        self.ecdsa = ecdsa_key
        return current_position

    def _process_ed25516(self, data):
        """ Parses ed25516 keys.

        There is no (apparent) way to validate ed25519 keys. This only
        checks data length (256 bits), but does not try to validate
        the key in any way.
        """

        current_position, verifying_key = self._unpack_by_int(data, 0)
        verifying_key_length = len(verifying_key) * 8
        verifying_key = self._parse_long(verifying_key)

        if verifying_key < 0:
            raise InvalidKeyException("ed25519 verifying key must be >0.")

        self.bits = verifying_key_length
        if self.bits != 256:
            raise InvalidKeyLengthException("ed25519 keys must be 256 bits (was %s bits)" % self.bits)
        return current_position

    def _process_key(self, data):
        if self.key_type == b"ssh-rsa":
            return self._process_ssh_rsa(data)
        elif self.key_type == b"ssh-dss":
            return self._process_ssh_dss(data)
        elif self.key_type.strip().startswith(b"ecdsa-sha"):
            return self._process_ecdsa_sha(data)
        elif self.key_type == b"ssh-ed25519":
            return self._process_ed25516(data)
        else:
            raise NotImplementedError("Invalid key type: %s" % self.key_type)

    def parse(self, keydata=None):
        """ Validates SSH public key

        Throws exception for invalid keys. Otherwise returns None.

        Populates key_type, bits and bits fields.

        For rsa keys, see field "rsa" for raw public key data.
        For dsa keys, see field "dsa".
        For ecdsa keys, see field "ecdsa". """
        if keydata is None:
            if self.keydata is None:
                raise ValueError("Key data must be supplied either in constructor or to parse()")
            keydata = self.keydata
        else:
            self.reset()
            self.keydata = keydata

        if keydata.startswith("---- BEGIN SSH2 PUBLIC KEY ----"):
            # SSH2 key format
            key_type = None  # There is no redundant key-type field - skip comparing plain-text and encoded data.
            pubkey_content = ""
            for line in keydata.split("\n"):
                if ":" in line:  # key-value lines
                    continue
                if "----" in line:  # begin/end lines
                    continue
                pubkey_content += line
        else:
            key_parts = self._split_key(keydata)
            key_type = key_parts[0]
            pubkey_content = key_parts[1]

        self._decoded_key = self.decode_key(pubkey_content)

        # Check key type
        current_position, unpacked_key_type = self._unpack_by_int(self._decoded_key, 0)
        if key_type is not None and key_type != unpacked_key_type.decode():
            raise InvalidTypeException("Keytype mismatch: %s != %s" % (key_type, unpacked_key_type))

        self.key_type = unpacked_key_type

        key_data_length = self._process_key(self._decoded_key[current_position:])
        current_position = current_position + key_data_length

        if current_position != len(self._decoded_key):
            raise MalformedDataException("Leftover data: %s bytes" % (len(self._decoded_key) - current_position))
