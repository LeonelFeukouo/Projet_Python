from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, NoEncryption, PublicFormat)


def MakeReq(userId, pseudo):
    private_key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048,
        backend = default_backend()
    )

    builder = x509.CertificateSigningRequestBuilder()
    mail = pseudo+'@tekup.leo'
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, mail),
        ]))
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,        
    )
    request = builder.sign(
        private_key, hashes.SHA256(), default_backend()
    )
    
    f1 = 'Certificates/'+userId+'.req'
    with open(f1, 'wb') as f:
        f.write(request.public_bytes(Encoding.PEM))

    f2 = 'Certificates/'+userId+'.key'
    with open(f2, 'wb') as f:
        f.write(private_key.private_bytes(Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL, NoEncryption()))

