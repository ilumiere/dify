import hashlib

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from extensions.ext_redis import redis_client
from extensions.ext_storage import storage
from libs import gmpy2_pkcs10aep_cipher

def generate_key_pair(tenant_id):
    """
    生成 RSA 密钥对并将其存储在指定路径中。

    该函数的主要用途是为指定的租户生成一对 RSA 密钥（公钥和私钥），并将私钥存储在指定的文件路径中。公钥则作为函数的返回值返回。

    参数:
    tenant_id (str): 租户的唯一标识符，用于生成密钥存储路径。

    返回值:
    str: 生成的公钥，以 PEM 格式编码的字符串。
    """

    # 生成一个 2048 位的 RSA 私钥
    private_key = RSA.generate(2048)

    # 从私钥中提取公钥
    public_key = private_key.publickey()

    # 将私钥和公钥导出为 PEM 格式的字节串
    pem_private = private_key.export_key()
    pem_public = public_key.export_key()

    # 构造私钥的存储路径，路径中包含租户 ID
    filepath = "privkeys/{tenant_id}".format(tenant_id=tenant_id) + "/private.pem"

    # 将私钥保存到指定的文件路径中
    storage.save(filepath, pem_private)

    # 返回公钥，将其从字节串解码为字符串
    return pem_public.decode()



prefix_hybrid = b"HYBRID:"


def encrypt(text, public_key):
    """
    使用混合加密算法对给定的文本进行加密。

    该函数的主要用途是使用混合加密算法对输入的文本进行加密。首先，使用 AES 算法生成一个随机的对称密钥，并使用该密钥对文本进行加密。然后，使用 RSA 算法对 AES 密钥进行加密。最后，将加密后的 AES 密钥、AES 算法的 nonce、tag 以及加密后的文本组合在一起，并添加一个前缀返回。

    参数:
    text (str): 需要加密的文本。
    public_key (str 或 bytes): 用于加密 AES 密钥的 RSA 公钥。如果传入的是字符串，会自动将其编码为字节串。

    返回值:
    bytes: 加密后的数据，包含前缀、加密后的 AES 密钥、nonce、tag 以及加密后的文本。
    """

    # 如果传入的公钥是字符串，将其编码为字节串
    if isinstance(public_key, str):
        public_key = public_key.encode()

    # 生成一个随机的 16 字节 AES 密钥
    aes_key = get_random_bytes(16)

    # 使用 AES 算法创建一个加密器，模式为 EAX
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)

    # 使用 AES 加密器对文本进行加密，并生成 tag
    ciphertext, tag = cipher_aes.encrypt_and_digest(text.encode())

    # 导入 RSA 公钥
    rsa_key = RSA.import_key(public_key)

    # 使用 RSA 算法创建一个加密器
    cipher_rsa = gmpy2_pkcs10aep_cipher.new(rsa_key)

    # 使用 RSA 加密器对 AES 密钥进行加密
    enc_aes_key = cipher_rsa.encrypt(aes_key)

    # 将加密后的 AES 密钥、nonce、tag 以及加密后的文本组合在一起
    encrypted_data = enc_aes_key + cipher_aes.nonce + tag + ciphertext

    # 添加前缀并返回加密后的数据
    return prefix_hybrid + encrypted_data

def get_decrypt_decoding(tenant_id):
    """
    获取指定租户的解密密钥和RSA加密器。

    该函数的主要用途是从缓存或存储中获取指定租户的私钥，并创建一个RSA加密器。如果私钥不在缓存中，则从存储中加载，并将其缓存一段时间以提高后续访问的效率。

    参数:
    tenant_id (str): 租户的唯一标识符。

    返回值:
    tuple: 包含两个元素的元组，第一个元素是导入的RSA密钥对象，第二个元素是使用该密钥创建的RSA加密器对象。
    """

    # 构建私钥文件路径
    filepath = "privkeys/{tenant_id}/private.pem".format(tenant_id=tenant_id)

    # 使用文件路径的哈希值作为缓存键
    cache_key = "tenant_privkey:{hash}".format(hash=hashlib.sha3_256(filepath.encode()).hexdigest())

    # 尝试从Redis缓存中获取私钥
    private_key = redis_client.get(cache_key)

    # 如果缓存中没有私钥，则从存储中加载
    if not private_key:
        try:
            private_key = storage.load(filepath)
        except FileNotFoundError:
            # 如果文件不存在，抛出PrivkeyNotFoundError异常
            raise PrivkeyNotFoundError("Private key not found, tenant_id: {tenant_id}".format(tenant_id=tenant_id))

        # 将加载的私钥缓存到Redis中，缓存时间为120秒
        redis_client.setex(cache_key, 120, private_key)

    # 导入私钥并创建RSA密钥对象
    rsa_key = RSA.import_key(private_key)

    # 使用RSA密钥对象创建RSA加密器
    cipher_rsa = gmpy2_pkcs10aep_cipher.new(rsa_key)

    # 返回RSA密钥对象和RSA加密器对象
    return rsa_key, cipher_rsa


def decrypt_token_with_decoding(encrypted_text, rsa_key, cipher_rsa):
    """
    使用RSA密钥和AES密钥解密加密文本。

    该函数的主要用途是解密使用RSA和AES混合加密的文本。首先检查加密文本是否以特定前缀开头，如果是，则使用AES密钥解密；否则，直接使用RSA密钥解密。

    参数:
    encrypted_text (str): 加密后的文本。
    rsa_key (RSA.RsaKey): RSA密钥对象，用于解密AES密钥。
    cipher_rsa (PKCS1_OAEP.PKCS1OAEP_Cipher): 使用RSA密钥创建的加密器对象，用于解密AES密钥。

    返回值:
    str: 解密后的明文文本。
    """

    # 检查加密文本是否以混合加密前缀开头
    if encrypted_text.startswith(prefix_hybrid):
        # 去除前缀，获取实际的加密数据
        encrypted_text = encrypted_text[len(prefix_hybrid) :]

        # 提取加密的AES密钥、nonce、tag和密文
        enc_aes_key = encrypted_text[: rsa_key.size_in_bytes()]
        nonce = encrypted_text[rsa_key.size_in_bytes() : rsa_key.size_in_bytes() + 16]
        tag = encrypted_text[rsa_key.size_in_bytes() + 16 : rsa_key.size_in_bytes() + 32]
        ciphertext = encrypted_text[rsa_key.size_in_bytes() + 32 :]

        # 使用RSA密钥解密AES密钥
        aes_key = cipher_rsa.decrypt(enc_aes_key)

        # 使用解密后的AES密钥、nonce和AES模式创建AES加密器
        cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)

        # 解密并验证密文
        decrypted_text = cipher_aes.decrypt_and_verify(ciphertext, tag)
    else:
        # 如果加密文本不以混合加密前缀开头，直接使用RSA密钥解密
        decrypted_text = cipher_rsa.decrypt(encrypted_text)

    # 返回解密后的明文文本
    return decrypted_text.decode()



def decrypt(encrypted_text, tenant_id):
    """
    使用租户ID解密加密文本。

    该函数的主要用途是根据提供的租户ID获取相应的RSA密钥和加密器，然后使用这些密钥和加密器解密加密文本。

    参数:
    encrypted_text (str): 加密后的文本，需要解密。
    tenant_id (str): 租户ID，用于获取相应的RSA密钥和加密器。

    返回值:
    str: 解密后的明文文本。
    """

    # 根据租户ID获取RSA密钥和RSA加密器对象
    rsa_key, cipher_rsa = get_decrypt_decoding(tenant_id)

    # 使用获取的RSA密钥和加密器对象解密加密文本
    return decrypt_token_with_decoding(encrypted_text, rsa_key, cipher_rsa)


class PrivkeyNotFoundError(Exception):
    """
    自定义异常类，用于在找不到私钥时抛出。

    该类继承自 Python 内置的 Exception 类，用于在 RSA 加密/解密过程中，当无法找到所需的私钥时抛出异常。
    通过使用自定义异常，可以更清晰地标识和处理与私钥相关的错误情况。
    """
    pass
