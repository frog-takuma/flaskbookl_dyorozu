from flask_wtf.file import FileAllowed, FileField, FileRequired
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import SubmitField


class UploadSoundForm(FlaskForm):
    # ファイルフィールドに必要なバリデーションを設定する
    sound = FileField(
        validators=[
            FileRequired("音源ファイルを指定してください。"),
            FileAllowed(["audio", "mpeg", "mp3"], "サポートされていない拡張子です。"),
        ]
    )
    submit = SubmitField("アップロード")


class DetectorForm(FlaskForm):
    submit = SubmitField("文字起こし")


class DeleteForm(FlaskForm):
    submit = SubmitField("削除")
