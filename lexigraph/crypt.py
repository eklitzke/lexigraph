import re
import zlib
import struct
import hashlib
import binascii

from level import CRYPT_SALT

MAXVAL = (1 << 32) - 1

for char in 'HILQ':
	if struct.calcsize(char) == 4:
		U32T = char
		break

for char in 'HILQ':
	if struct.calcsize(char) == 8:
		U64T = char
		break

def encode(num):
	if num <= 0 or num > MAXVAL:
		raise ValueError('Invalid number: only input in the range [1, %d] allowed' % (MAXVAL,))
	s1 = hashlib.md5(struct.pack(U64T, num)).digest()[:8]
	s1n, = struct.unpack(U64T, s1)
	s2 = hashlib.md5(s1 + CRYPT_SALT).digest()[:4]
	s2n, = struct.unpack(U32T, s2)
	if s2n > num:
		s2 = struct.pack(U32T, s2n - num)
	else:
		s2 = struct.pack(U32T, s2n + num)
	s3 = struct.pack(U32T, zlib.adler32(s1 + s2) & 0xffffffff)
	buf = binascii.b2a_base64(s1 + s2 + s3).rstrip('=\n')
	return buf.replace('+', '-').replace('/', '_')

def decode(buf, validate=True):
	if len(buf) != 22:
		raise ValueError('Encoded value had incorrect length')
	buf = buf.replace('_', '/').replace('-', '+') + '=='
	try:
		buf = binascii.a2b_base64(buf)
	except binascii.Error:
		raise ValueError('Invalid base64 data')
	s1, s2, s3 = buf[:8], buf[8:12], buf[12:]
	if validate and s3 != struct.pack(U32T, zlib.adler32(s1 + s2) & 0xffffffff):
		raise ValueError('Checksum failed for encoded data')
	s2n, = struct.unpack(U32T, s2)
	my_s2 = hashlib.md5(s1 + CRYPT_SALT).digest()[:4] 
	my_s2n, = struct.unpack(U32T, my_s2)
	return abs(s2n - my_s2n)
