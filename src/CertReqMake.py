from cryptography import x509
from OpenSSL import crypto
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
import datetime
import uuid


def MakeCert(userId):
    f1 = 'Certificates/'+userId+'.req'
    pem_csr = open(f1, 'rb').read()
    csr = x509.load_pem_x509_csr(pem_csr, default_backend())

    pem_cert = open('Certificates/ca.crt', 'rb').read()
    ca = x509.load_pem_x509_certificate(pem_cert, default_backend())

    pem_key = open('Certificates/ca.key','rb').read()
    ca_key = serialization.load_pem_private_key(pem_key, password=None, backend=default_backend())

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(csr.subject)
    builder = builder.issuer_name(ca.subject)
    builder = builder.not_valid_before(datetime.datetime.now())
    builder = builder.not_valid_after(datetime.datetime.now() + datetime.timedelta(days=7))
    builder = builder.public_key(csr.public_key())
    builder = builder.serial_number(int(uuid.uuid4()))

    for ext in csr.extensions:
        builder = builder.add_extension(ext.value, ext.critical)

    certificate = builder.sign(
        private_key = ca_key,
        algorithm = hashes.SHA256(),
        backend = default_backend()
    )
    
    f2 = 'Certificates/'+userId+'.crt'
    with open(f2, 'wb') as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM)) 

