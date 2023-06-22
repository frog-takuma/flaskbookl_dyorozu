import uuid
from pathlib import Path

import whisper
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   url_for)
from flask_login import current_user, login_required

from apps.app import db
from apps.crud.models import User
from apps.whisper.forms import DeleteForm, DetectorForm, UploadSoundForm
from apps.whisper.models import UserSound, UserSoundTag

whi = Blueprint("whisper", 
                __name__, 
                template_folder="templates", 
                static_folder="static")


@whi.route("/")
def index():

    user_sounds = (
        db.session.query(User, UserSound)
        .join(UserSound)
        .filter(User.id == UserSound.user_id)
        .all()
    )
    detector_form = DetectorForm()
    delete_form = DeleteForm()

    return render_template(
        "whisper/index.html",
        user_sounds=user_sounds,
        detector_form=detector_form,
        delete_form=delete_form,
    )


@whi.route("/upload", methods=["GET", "POST"])
# ログイン必須とする
@login_required
def upload_sound():
    # UploadImageFormを利用してバリデーションをする
    form = UploadSoundForm()
    if form.validate_on_submit():
        # アップロードされた画像ファイルを取得する
        file = form.sound.data

        # ファイルのファイル名と拡張子を取得し、ファイル名をuuidに変換する
        ext = Path(file.filename).suffix
        sound_uuid_file_name = str(uuid.uuid4()) + ext

        # 画像を保存する
        sound_path = Path(current_app.config["UPLOAD_FOLDER_SOUND"], 
                          sound_uuid_file_name)
        
        file.save(sound_path)

        # DBに保存する
        sound_image = UserSound(user_id=current_user.id, 
                                sound_path=sound_uuid_file_name)
        print("===ans===", sound_image)
        db.session.add(sound_image)
        db.session.commit()

        return redirect(url_for("whisper.index"))
    return render_template("whisper/upload.html", form=form)


@whi.route("/sounds/delete/<string:sound_id>", methods=["POST"])
@login_required
def delete_sound(sound_id):
    try:
        
        db.session.query(UserSoundTag).filter(
            UserSoundTag.user_sound_id == sound_id
        ).delete()

        db.session.query(UserSound).filter(UserSound.id == sound_id).delete()
        db.session.commit()
    except Exception as e:
        flash("画像削除処理でエラーが発生しました。")
        # エラーログ出力
        current_app.logger.error(e)
        db.session.rollback()
    return redirect(url_for("whisper.index"))


def save_detected_sound_tags(user_sound, tags, detected_sound_file_name):
    # 検知後画像の保存先パスをDBに保存する
    user_sound.sound_path = detected_sound_file_name
    # 検知フラグをTrueにする
    user_sound.is_detected = True
    db.session.add(user_sound)
    # user_images_tagsレコードを作成する
    for tag in tags:
        user_sound_tag = UserSoundTag(user_sound_id=user_sound.id, tag_name=tag)
        db.session.add(user_sound_tag)
    db.session.commit()


@whi.route("/detect/<string:sound_id>", methods=["POST"])
# login_requiredデコレーターをつけてログイン必須とする
@login_required
def detect(sound_id):
    # user_imagesテーブルからレコードを取得する
    user_sound = db.session.query(UserSound).filter(UserSound.id == sound_id).first()
    if user_sound is None:
        flash("音源が存在しません。")
        return redirect(url_for("whisper.index"))

    # 物体検知対象の画像パスを取得する
    target_sound_path = Path(current_app.config["UPLOAD_FOLDER_SOUND"], 
                             user_sound.sound_path)
    # 物体検知を実行してタグと変換後の画像パスを取得する
    tags, detected_sound_file_name = exec_whisper(target_sound_path)

    try:
        # データベースにタグと変換後の画像パス情報を保存する
        save_detected_sound_tags(user_sound, [tags], detected_sound_file_name)
    except Exception as e:
        flash("物体検知処理でエラーが発生しました。")
        # ロールバックする
        db.session.rollback()
        # エラーログ出力
        current_app.logger.error(e)
        return redirect(url_for("whisper.index"))
    return redirect(url_for("whisper.index"))


def exec_whisper(target_sound_path):
    print("path", target_sound_path)
    print("type", type(target_sound_path))
    # ラベルの読み込み
    model = whisper.load_model("base")
    # result = model.transcribe("準備したファイル名を指定") # 今回の記事ではtest.m4aを用います。
    result = model.transcribe(str(target_sound_path))
    print(result["text"])

    # 検知後の画像ファイル名を生成する
    detected_sound_file_name = str(uuid.uuid4()) + ".jpg"

    # 変換後の画像ファイルを保存先へコピーする
    return result["text"], detected_sound_file_name
