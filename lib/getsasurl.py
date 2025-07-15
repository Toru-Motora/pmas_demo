from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas, generate_container_sas, ContainerSasPermissions
from datetime import datetime, timedelta
import base64  # Base64デコード用

def get_blob_sas_url(
    account_name: str,
    account_key: str,
    container_name: str,
    blob_name: str,
    permission: BlobSasPermissions = BlobSasPermissions(read=True),
    expiry_hours: int = 1,
    start_time: datetime = None
) -> str:
    """
    指定したパラメータで特定のBLOBに対するSAS URLを生成します。

    Args:
        account_name (str): ストレージアカウント名。
        account_key (str): アカウントキー。
        container_name (str): 対象のコンテナ名。
        blob_name (str): 対象のBLOB名。
        permission (BlobSasPermissions): SASの権限（例: read=True, write=True）。デフォルトは読み取り専用。
        expiry_hours (int): SASの有効期限（時間単位）。デフォルトは1時間。
        start_time (datetime): SASの開始時刻。省略時は現在時刻（UTC）。

    Returns:
        str: 生成されたBLOBに対するSAS URL。
    """
    # start_timeが指定されていない場合は現在時刻より5分前を使用（時刻のずれを考慮）
    start_time = datetime.utcnow() - timedelta(minutes=5) if start_time is None else start_time
    expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)  # 現在時刻から計算

    try:
        # アカウントキーをBase64デコード（既にデコードされている場合は不要）
        # Azure SDKは内部でデコードするため、通常は不要
        # account_key_bytes = base64.b64decode(account_key)
        
        # デバッグ情報を出力
        print(f"BLOB SAS生成パラメータ:")
        print(f"account_name: {account_name}")
        print(f"container_name: {container_name}")
        print(f"blob_name: {blob_name}")
        print(f"permission: {permission}")
        print(f"start_time: {start_time}")
        print(f"expiry_time: {expiry_time}")
        
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=permission,
            expiry=expiry_time,
            start=start_time,
            protocol="https"  # プロトコルを明示的に指定
        )
    except Exception as e:
        print(f"BLOB SAS生成中にエラーが発生: {e}")
        raise

    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"


def get_container_sas_url(
    account_name: str,
    account_key: str,
    container_name: str,
    permission: ContainerSasPermissions = ContainerSasPermissions(read=True, list=True, write=True, delete=True),
    expiry_hours: int = 1,
    start_time: datetime = None
) -> str:
    """
    指定したパラメータでコンテナ全体に対するSAS URLを生成します。

    Args:
        account_name (str): ストレージアカウント名。
        account_key (str): アカウントキー。
        container_name (str): 対象のコンテナ名。
        permission (ContainerSasPermissions): SASの権限（例: read=True, list=True, write=True）。デフォルトは読み取りとリスト。
        expiry_hours (int): SASの有効期限（時間単位）。デフォルトは1時間。
        start_time (datetime): SASの開始時刻。省略時は現在時刻（UTC）。

    Returns:
        str: 生成されたコンテナに対するSAS URL。
    """
    # start_timeが指定されていない場合は現在時刻より5分前を使用（時刻のずれを考慮）
    start_time = datetime.utcnow() - timedelta(minutes=5) if start_time is None else start_time
    expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)  # 現在時刻から計算

    # デバッグ情報を出力
    print(f"Container SAS生成パラメータ:")
    print(f"account_name: {account_name}")
    print(f"container_name: {container_name}")
    print(f"permission: {permission}")
    print(f"start_time: {start_time}")
    print(f"expiry_time: {expiry_time}")
    
    # $rootコンテナの場合の特別処理
    if container_name == "$root":
        print("$rootコンテナが指定されました - 特別な処理を適用します")
        container_name = ""
    sas_token = generate_container_sas(
        account_name=account_name,
        container_name=container_name,
        account_key=account_key,
        permission=permission,
        expiry=expiry_time,
        start=start_time,
        protocol="https",  # プロトコルを明示的に指定
        cache_control=None,  # キャッシュ制御を明示的に指定
        content_disposition=None,  # コンテンツディスポジションを明示的に指定
        content_encoding=None,  # コンテンツエンコーディングを明示的に指定
        content_language=None,  # コンテンツ言語を明示的に指定
        content_type=None  # コンテンツタイプを明示的に指定
    )

    # SAS URLのみ  
    return f"https://{account_name}.blob.core.windows.net/{container_name}?{sas_token}"

    # SAS URL + リスト
    # return f"https://{account_name}.blob.core.windows.net/{container_name}?{sas_token}&restype=container&comp=list" 
    




#     # 単体実行用（検証用パラメータでSAS URLを出力）
# def main():
#     """
#     このモジュールを直接実行した場合のテスト用メイン関数。
#     デフォルト値を使ってコンテナSAS URLを生成し、出力します。
#     """
#     container_sas_url = get_container_sas_url(account_name: str,account_key: str,container_name: str)
#     print(f"Container SAS URL: {container_sas_url}")
#     return container_sas_url

# if __name__ == "__main__":
#     main()

# """
# 【外部からの呼び出し例】

# from getsasurl import get_container_sas_url

# sas_url = get_container_sas_url(
#     account_name="your_account_name",
#     account_key="your_account_key",
#     container_name="your_container_name",
#     # permissionやexpiry_hoursなど必要に応じて追加可能
# )
# print(sas_url)
# """
