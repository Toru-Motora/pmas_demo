import os
import logging
import json
import sys
import traceback
import re
from pickle import TRUE
from sys import addaudithook
from flask import Flask, jsonify
from threading import Thread
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack.pm_assistant_form_open_button_block import pm_assistant_form_open_button_block
from slack.pm_assistant_form_block import pm_assistant_form_block
from logging import Logger
import requests
from lib.getsasurl import get_container_sas_url

# ロガーを設定（これにより、Boltの内部ログも表示されやすくなります）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UIを含むログ出力モード
# DEBUG_MODE = True
DEBUG_MODE = False

# 環境変数からトークンを読み込む
# xoxb- から始まる Bot User OAuth Token
bot_token = os.environ.get("SLACK_BOT_TOKEN")
# xapp- から始まる App-Level Token (ソケットモード用 / Basic Information)
app_token = os.environ.get("SLACK_APP_TOKEN")

if DEBUG_MODE:
    # Slack認証用トークン設定確認
    if not bot_token:
        logger.error("SLACK_BOT_TOKEN が設定されていません。")
    if not app_token:
        logger.error("SLACK_APP_TOKEN が設定されていません。")


# 共通定数
HSQ_SIGN_USER = "toru_motora+llm@saison-technology.com"
HSQ_SIGN_PASSWORD = os.environ.get("HSQ_SIGNING_SECRET")
HSQ_API_URL = "https://app.square.hulft.com/v1/users/login"


# Flaskアプリの初期化（ローカル実行用）
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return jsonify({
        "status": "running",
        "app": "炎上リスク分析",
        "description": "炎上リスク分析アプリが実行中です"
    })

@flask_app.route("/health")
def health():
    return jsonify({"status": "healthy"})

# Slackボットトークンとソケットモードハンドラーを使ってアプリを初期化
app = App(token=bot_token)

def get_access_token():
    """
    login APIを使ってHULFT Square認証情報からアクセストークンを取得する
    """
    url = HSQ_API_URL
    body = {
        "email": HSQ_SIGN_USER,
        "password": HSQ_SIGN_PASSWORD
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        logger.info("HULFT Square認証APIにリクエストを送信します: %s", url)
        response = requests.post(url, json=body, headers=headers, verify=False, timeout=30)
        logger.info("HULFT Square認証APIのレスポンスステータス: %s", response.status_code)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"access_token_data: {data}")
        logger.info("アクセストークン取得に成功しました")
        # 必要なキーが存在するかチェック
        if 'accessToken' not in data or 'challenge' not in data:
            logger.error("レスポンスにaccessTokenまたはchallengeが含まれていません: %s", data)
            raise ValueError("accessTokenまたはchallengeがレスポンスに含まれていません")
        return data['accessToken'], data['challenge']
    except requests.exceptions.RequestException as e:
        logger.error("HULFT Square認証APIでリクエストエラーが発生しました: %s", e)
        raise
    except ValueError as ve:
        logger.error("HULFT Square認証APIのレスポンスエラー: %s", ve)
        raise

def update_refresh_token(access_token):
    """アクセストークンを使いリフレッシュトークンを更新"""
    url = 'https://app.square.hulft.com/v1/rest-api-token'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.post(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['accessToken']
    except requests.exceptions.RequestException as e:
        raise


def invoke_hsq_translation_api(
    access_token: str,
    execution_user: str,
    audio_file_box_id: str,
    input_container_sas_url: str,
    output_container_sas_url: str,
    slack_channel_id: str,
    slack_channel_member: str,
    option: str = ""
):
    """
    HULFT Squareの音声ファイル変換API（pmassistantエンドポイント）にリクエストを送信し、
    音声ファイル情報・SAS URL・Slackチャンネル情報などを指定してAPIを呼び出します。
    レスポンスとしてJSONを返します。
    例外発生時には不足しているパラメータをログに出力します。

    Args:
        access_token (str): Bearerトークン
        execution_user (str): 実行ユーザー名
        audio_file_box_id (str): 音声ファイルのBoxId。https://sisco001.ent.box.com/file/'BoxId'の'BoxId'部分
        input_container_sas_url (str): 入力先コンテナのSAS URL
        output_container_sas_url (str): 出力先コンテナのSAS URL
        slack_channel_id (str): SlackチャンネルID
        slack_channel_member (str): Slackチャンネルメンバー（例: '@junichi_kudo @shingo_kawahara @naoto_minagawa'）
        option (str): 個別指定のPJ分析アウトライン（任意）

    Returns:
        dict: APIレスポンスのJSON
    """

    url = "https://a00001-21.square.hulft.com/PMAssistant-dev/pmassistant"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-HSQ-Async": "true"
    }
    body = {
        "executionUser": execution_user,
        "audioFileBoxId": audio_file_box_id,
        "inputContainerSasUrl": input_container_sas_url,
        "outputContainerSasUrl": output_container_sas_url,
        "slackChannelId": slack_channel_id,
        "slackChannelMember": slack_channel_member,
        "option": option
    }

    try:
        response = requests.post(url, data=json.dumps(body), headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # パラメータの存在を確認
        
        missing_params = []
        if not access_token:
            missing_params.append("access_token")
        if not execution_user:
            missing_params.append("execution_user")
        if not audio_file_box_id:
            missing_params.append("audio_file_box_id")
        if not input_container_sas_url:
            missing_params.append("input_container_sas_url")
        if not output_container_sas_url:
            missing_params.append("output_container_sas_url")
        if not slack_channel_id:
            missing_params.append("slack_channel_id")
        if not slack_channel_member:
            missing_params.append("slack_channel_member")
        if missing_params:
            logging.error("以下のパラメータが不足しています: %s", ', '.join(missing_params))
        raise e

def ex_get_container_sas_url(container_name: str):
    """
    Azure Storageの指定されたコンテナのSAS URLを取得します。
    発行URLに対して"&restype=container&comp=list"を付記するとLIST形式で参照可能です。
    """
        
    # 環境変数から値を取得
    account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    
    # 環境変数の存在チェック
    if not account_name:
        raise ValueError("AZURE_STORAGE_ACCOUNT_NAME environment variable is not set")
    if not account_key:
        raise ValueError("AZURE_STORAGE_ACCOUNT_KEY environment variable is not set")
    
    print(f"アカウント名: {account_name}, コンテナ名: {container_name}")
    
    return get_container_sas_url(
        account_name=account_name,
        account_key=account_key,
        container_name=container_name
    )


# @app.command("/pmassistant_form_open")
@app.command("/pmassistant_form")
def post_pm_assistant_form_open_button_message(ack, say) -> None:
    """
    /pmassistant_form コマンドが実行された場合、フォームを開くボタンを含んだメッセージを送信します。
    member_joined_channel イベントで実行しようとしていましたが、イベントが発火せず、原因不明のためコマンドにしています。
    """
    ack()

    logger.info("コマンドが実行されました。")

    say(
        {
            "text": "炎上リスク分析用メッセージ",
            "blocks": pm_assistant_form_open_button_block(),
        }
    )


@app.action("pma-form-open-submit-button")
def handle_pma_form_open(ack, body, client, logger: Logger) -> None:
    """
    Slackチャンネル上で"開始する"ボタンが押された場合、入力フォームを開きます。
    """
    ack()

    logger.info("開始ボタンが押されました。")

    # 実行ユーザー
    slack_user = body["user"]
    slack_user_name = slack_user["name"]

    # 入力（audio）・出力（transcriptions）コンテナのSAS URL取得
    audio_container_sas_url = ex_get_container_sas_url("audio")
    transcriptions_container_sas_url = ex_get_container_sas_url("transcriptions")

    try:
        # チャンネルIDを取得
        channel_id = body.get("channel", {}).get("id")

        member_ids = []
        # チャンネル情報とメンバー情報をログ出力（任意で残す場合）
        if channel_id:
            try:
                # チャンネルメンバーの取得
                members_info = client.conversations_members(channel=channel_id)
                member_ids = members_info.get("members", [])
                
            except Exception as e:
                logger.warning("チャンネルメンバー取得時に例外が発生しました: %s", e)
            try:
                # チャンネル情報の取得
                try:
                    channel_info = client.conversations_info(channel=channel_id)
                    channel_name = channel_info["channel"].get("name")
                    logger.info("チャンネルID: %s, チャンネル名: %s", channel_id, channel_name)
                except Exception as e:
                    logger.warning("チャンネル情報取得時に例外が発生しました: %s", e)

                # メンバーの表示名もログ出力
                member_details = []
                for member_id in member_ids:
                    try:
                        user_info = client.users_info(user=member_id)
                        # 取得しやすい形式で表示名を取得（display_nameがあればそれを、なければreal_name、なければname）
                        user = user_info.get("user", {})
                        display_name = user.get("name", "")
                        member_details.append({"id": member_id, "display_name": display_name})
                    except Exception as e:
                        member_details.append({"id": member_id, "display_name": "名前取得失敗"})
                        logger.warning("ユーザー情報取得時に例外が発生しました: %s", e)
                logger.info("チャンネル参加メンバー一覧: %s", member_details)

            except Exception as e:
                logger.exception("チャンネル情報またはメンバー取得時に予期せぬ例外が発生しました: %s", e)



        else:
            logger.info("チャンネルIDが取得できませんでした。")

        # hidden値をjsonにまとめて次の画面に渡す
        hidden_values = {
            "audio_container_sas_url": audio_container_sas_url,
            "transcriptions_container_sas_url": transcriptions_container_sas_url,
            "channel_id": channel_id,
            "member_details": member_details
        }
        # pm_assistant_form_blockにメンバーIDリストを渡す
        # trigger_idは一度だけ使用可能
        client.views_open(
            trigger_id=body["trigger_id"],
            view=pm_assistant_form_block(slack_user["id"], member_ids, hidden_values),
        )
        logger.info("%s によって炎上リスク分析投稿フォームが開かれました。", slack_user_name)

    except Exception:
        logger.exception(
            "%s による炎上リスク分析投稿フォーム呼び出し時に例外が発生しました。",
            slack_user_name
        )


@app.view("pm_assistant_form")
def handle_pm_assistant_form_post(ack, body, view: dict, client, logger: Logger):
    """
    Slack上の入力フォーム上で"チェック"が選択された場合、
    入力情報をパラメータとしてHULFTSquareのジョブ起動エンドポイントにリクエストを発行します。
    """
    ack()
    
    slack_user = body["user"]
    
    # 各変数を定義
    view_state = view["state"]["values"]
    # MTGアウトライン（テキスト）
    agenda_text = view_state["agenda"][list(view_state["agenda"].keys())[0]]["value"]
    # Boxファイルパス（テキスト）
    box_file_path = view_state["box_url"][list(view_state["box_url"].keys())[0]]["value"]
    # private_metadataのパース
    


    private_metadata = json.loads(view.get("private_metadata", "{}"))
    audio_container_sas_url = private_metadata.get("audio_container_sas_url")
    transcriptions_container_sas_url = private_metadata.get("transcriptions_container_sas_url")
    channel_id_from_metadata = private_metadata.get("channel_id")
    member_details = private_metadata.get("member_details")

    try:
        #1.処理開始
        logger.info("炎上リスク分析機能を実行開始")
        
        logger.info("メッセージ送信実行、処理開始")
        #2 HSQトークン取得
        access_token, challenge = get_access_token()
        new_access_token = update_refresh_token(access_token)
        print(f"new_access_token: {new_access_token}")

        logger.info("HULFT Squareのトークン取得完了")

        if DEBUG_MODE:
            # 上のメッセージ送信形式に合わせて日本語で統一
            client.chat_postMessage(
                channel=channel_id_from_metadata,
                text=(
                    "HULFT Squareのトークンを取得しました。\n"
                    "----------------------------------------\n"
                    f"access_token（文字数）: `{len(access_token)}`\n"
                    "----------------------------------------\n"
                )
            )

        if DEBUG_MODE:
            client.chat_postMessage(
                channel=channel_id_from_metadata,
                text=(
                    "SAS URLを取得しました。\n"
                    "----------------------------------------\n"
                    f"audioコンテナSAS URL: {audio_container_sas_url}\n"
                    f"transcriptionsコンテナSAS URL: {transcriptions_container_sas_url}\n"
                    "----------------------------------------\n"
                )
            )
        logger.info("入力情報取得完了")

        # 入力データbox_file_pathのバリデーション
        box_domain = "https://sisco001.ent.box.com/file"

        # https://sisco001.ent.box.com/file以外ならエラー
        if not box_file_path.startswith(box_domain):
            raise ValueError("入力されたリンクが不正です。\n"
                             f"※'{box_domain}/XXXXX'の形式で入力してください。")
        
        # https://sisco001.ent.box.com/file/1931781410243 の file以降の数字を取得
        box_file_id = box_file_path.split('/')[-1]

        # "xxx.com/file/1934340618266?s=cxmxwccaqmbdzjpnhe80wtbtw25bwc59"のように、パラメータありの場合はパラメータを削除
        # box_file_idもパラメータを除去した形で取得する
        if "?" in box_file_path:
            box_file_path = box_file_path.split("?")[0]
        box_file_id = box_file_path.split('/')[-1]
        logger.info(f"BOX ID取得完了: {box_file_id}")


        slack_channel_menbers = [member["display_name"] for member in member_details]
        if DEBUG_MODE:
            client.chat_postMessage(
                channel=channel_id_from_metadata,
                text=(
                    "入力情報を取得しました。\n"
                    "----------------------------------------\n"
                    f"box_file_id: {box_file_id}\n"
                    f"execution_user: {slack_user["name"]}\n"
                    f"channel_id: {channel_id_from_metadata}\n"
                    f"slack_channel_menbers: {slack_channel_menbers}\n"
                    f"agenda_text: {agenda_text}\n"
                    "----------------------------------------\n"
                )
            )

        #3.HULFT Squareのジョブを叩く
        #文字列に変換
        slack_channel_members_str = ", ".join(slack_channel_menbers)
        print(f"slack_channel_members_str: {slack_channel_members_str}")

        logger.info("HULFT Squareのジョブ実行開始")

        res = invoke_hsq_translation_api(
            access_token=new_access_token,
            # new_access_token=refresh_token,
            audio_file_box_id=box_file_id,
            execution_user=slack_user["name"],
            input_container_sas_url=audio_container_sas_url,
            output_container_sas_url=transcriptions_container_sas_url,
            slack_channel_id=channel_id_from_metadata,
            slack_channel_member=slack_channel_members_str,
            option=agenda_text
        )
        logger.info("HULFT Squareのジョブ実行完了")

        if DEBUG_MODE:
            client.chat_postMessage(
                channel=channel_id_from_metadata,
                text="リクエストパラメーターは以下の通りです。\n"
                f"access_token: {new_access_token}\n"
                f"audio_file_box_id: {box_file_id}\n"
                f"execution_user: {slack_user["name"]}\n"
                f"input_container_sas_url: {audio_container_sas_url}\n"
                f"output_container_sas_url: {transcriptions_container_sas_url}\n"
                f"slack_channel_id: {channel_id_from_metadata}\n"
                f"slack_channel_member: {slack_channel_members_str}\n"
                f"option: {agenda_text}\n"
            )  

        # client.chat_postMessage(
        #     channel=channel_id_from_metadata,
        #     text="炎上リスク分析機能を実行中です:hourglass_flowing_sand:\nしばらくお待ちください…"
        # )       

        logger.info("炎上リスク分析HSQリクエスト完了")
    except:
        # エラーメッセージを画面に渡す
        exc_type, exc_value, _ = sys.exc_info()
        error_message = str(exc_value)
        
        client.chat_postMessage(
            channel=channel_id_from_metadata,
            text=f"\n 【エラー】炎上リスク分析機能実行処理を中断しました。\n理由：\n{error_message}\n"
        )

        logger.exception("炎上リスク分析機能実行時に例外が発生しました。")
        

# Socket Mode（SlackとのWebSocket通信）を開始するための関数
# Slack BoltのSocketModeHandlerを使い、appインスタンスとapp_tokenで
# リアルタイムなイベント受信・送信を可能にします。
# trace_enabled=Trueで詳細ログ、auto_reconnect_enabled=Trueで自動再接続を有効化しています。
def run_socket_mode():
    handler = SocketModeHandler(
        app=app,
        app_token=app_token,
        trace_enabled=True,
        auto_reconnect_enabled=True
    )
    handler.start()

if __name__ == "__main__":
    # 環境変数に基づいて実行モードを切り替え
    # ※ ローカルだとwebsocket通信（Socket Mode）が使えて、WebApp（Azure Web App）だと使えない事象があった
    # ・ローカル環境では、アプリケーションが直接外部とWebSocket通信を確立できるためSocket Modeが利用可能
    # ・一方、Azure Web AppなどのPaaS環境では、外部からのWebSocket通信が制限されていたり、
    # 　プロキシやロードバランサーの影響でソケット通信が安定して確立できない場合が多い。
    # ・そのため、WebApp環境ではHTTPリクエスト（Events API）を受け付けるFlaskサーバーも併用する「ハイブリッドモード」を実装
    is_azure_webapp = os.environ.get("AZURE_WEBAPP_MODE", "").lower() == "true"
    
    if is_azure_webapp:
        # Azure Web App モードで起動（ハイブリッドモード）
        logger.info("Azure Web App モードで起動しています")
        # Socket Modeを別スレッドで実行
        socket_thread = Thread(target=run_socket_mode)
        socket_thread.daemon = True
        socket_thread.start()
        
        # Flaskサーバーを起動（Azure App Serviceが期待するポート8000で）
        port = int(os.environ.get("PORT", 8000))
        flask_app.run(host="0.0.0.0", port=port)
    else:
        # ローカル環境上の実行
        logger.info("ローカルモードで起動しています。")
        # 従来通りSocket Modeのみで実行
        run_socket_mode()