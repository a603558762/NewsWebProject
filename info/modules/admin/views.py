from flask import render_template

from info.modules.admin import admin_blu

@admin_blu.route('/')
def index():

    return render_template('admin/index.html')

@admin_blu.route('/login')
def login():


    return render_template('admin/login.html')