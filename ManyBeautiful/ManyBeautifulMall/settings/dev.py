"""
Django settings for ManyBeautifulMall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import datetime
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import sys
# sys.path: python解释器查找包的路径
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, BASE_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '79@+w9!(ft_q*=%0ilvacg5hgwon=-b)$*cx6x$6_1ss-!h^y^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 增加可以访问后端的域名
ALLOWED_HOSTS = [
    'api.meiduo.site',
    '127.0.0.1',
    'localhost',
    'www.meiduo.site'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'rest_framework',
    'corsheaders',  # 使用CORS来解决后端对跨域访问的支持
    'verifications.apps.VerificationsConfig',
    'oauth.apps.OauthConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ManyBeautifulMall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ManyBeautifulMall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'meiduo',  # 数据库用户名
        'PASSWORD': 'meiduo',  # 数据库用户密码
        'NAME': 'md_mall'  # 数据库名字
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 配置缓存
CACHES = {
    #  配置缓存，必须要有default
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "sms_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# 设置session的保存方案
# 指定session使用缓存进行保存,缓存保存在redis中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# 添加日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 关闭已存在的日志器
    'formatters': {  # 日志信息显示格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 日志过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志  在debug模试下
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "../logs/meiduo.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}


REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'utils.exceptions.exception_handler',
    # 身份认证
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 前后段分离使用jwt
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        # 访问admin后台时使用session
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}


JWT_AUTH = {
    # 指明token的有效期
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 指定返回类型
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',
}

# 使django的认证系统使用我们自定义的模型类
# 应用名.模型类名
# 设置之后,进行数据库迁移
AUTH_USER_MODEL = "users.User"


# 添加白名单  写鬣域名可以访问`后端接口
CORS_ORIGIN_WHITELIST = (
    'www.meiduo.site:8080',
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie


# 自定义认证后端,用于登陆时的认证
AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',
]

# QQ登陆参数
# 申请QQ登录成功后，分配给应用的appid。
QQ_CLIENT_ID = '101474184'
# 申请QQ登录成功后，分配给网站的appkey
QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
# 成功授权后的回调地址，必须是注册appid时填写的主域名下的地址
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
QQ_STATE = '/'


# # 微信登陆参数
# # 申请微信登录成功后，分配给应用的appid。
# WEIXIN_CLIENT_ID = ''
# # 申请微信登录成功后，分配给网站的appkey
# WEIXIN_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
# # 成功授权后的回调地址，必须是注册appid时填写的主域名下的地址
# WEIXIN_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
# WEIXIN_STATE = '/'
