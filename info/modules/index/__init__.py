# 蓝图的抽取
from flask import Blueprint
Index_blu=Blueprint('index',__name__,url_prefix='')
from .views import *





