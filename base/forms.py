from wtforms.csrf.session import SessionCSRF
from wtforms import Form
from datetime import timedelta


class YHKForm(Form):
    """
    基础Form
    """

    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = b'2K7715f4F1d1HEXGe69PRO2X2b8EG85U62Rb8U42c'
        csrf_time_limit = timedelta(minutes=20)  # 20分钟内有效

