from datetime import datetime

from apps.app import db


class UserSound(db.Model):
    __tablename__ = "user_sounds"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    sound_path = db.Column(db.String)  # sound_path列を追加
    is_detected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class UserSoundTag(db.Model):
    # テーブル名を指定する
    __tablename__ = "user_sound_tags"
    id = db.Column(db.Integer, primary_key=True)
    # user_image_idはuser_imagesテーブルのidカラムの外部キーとして設定する
    user_sound_id = db.Column(db.String, db.ForeignKey("user_sounds.id"))
    tag_name = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
