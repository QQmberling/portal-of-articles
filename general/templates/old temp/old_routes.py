# @app.after_request
# def redirect_to_signin(response):
#     if response.status_code == 401:
#         #print('status code', response.status_code)
#         return redirect(url_for('login_page') + '?next=' + request.url)
#
#     #print(response.status_code, 'response')
#     #print(request.referrer, 'after request refferer')
#     #print(request.url, 'url')
#     return response

# def redirect_back():
#     for target in request.referrer:
#         if not target:
#             continue
#         redirect(target)


# @app.route('/base2')
# def base2():
#     context = {'user_is_authenticated': current_user.is_authenticated}
#     return render_template('base.html', context=context)
#
# @app.route('/base22')
# def base22():
#     context = {'user_is_authenticated': current_user.is_authenticated}
#     return render_template('base22.html', context=context)


# @app.route('/register', methods=['POST', 'GET'])
# def register():
#     context = {'user_is_authenticated': current_user.is_authenticated}
#
#     login = request.form.get('login')
#     password = request.form.get('password')
#     password2 = request.form.get('password2')
#
#     if request.method == 'POST':
#         if not (login or password2 or password):
#             flash('Please fill all fields!')
#         elif password != password2:
#             flash('Passwords are not equal!')
#         else:
#             hash_pwd = generate_password_hash(password)
#             new_user = User(login=login, password=hash_pwd)
#             try:
#                 db.session.add(new_user)
#                 db.session.commit()
#                 flash('Регистрация успешно завершена. Можете авторизоваться.')
#             except:
#                 return 'При регистрации возникла ошибка'
#
#             return redirect(url_for('login_page'))
#
#     return render_template('register.html', context=context)

# @app.route('/login', methods=['POST', 'GET'])
# def login_page():
#     context = {'user_is_authenticated': current_user.is_authenticated}
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     login = request.form.get('login')
#     password = request.form.get('password')
#
#     if login and password:
#         user = User.query.filter_by(login=login).first()
#         if user and check_password_hash(user.password, password):
#             rm = True if request.form.get('remainme') else False
#             login_user(user, rm)
#             #return redirect(url_for('index'))
#             return redirect(request.args.get("next") or url_for("index"))
#         else:
#             flash('Login or password incorrect')
#     else:
#         flash('Please fill login and password fields')
#     return render_template('login.html', context=context)

# @app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
# @login_required
# def post_update(id):
#     context = {'user_is_authenticated': current_user.is_authenticated, 'legend': 'Редактирование статьи'}
#
#     article = Article.query.get(id)
#     if request.method == 'POST':
#         article.title = request.form['title']
#         article.intro = request.form['intro']
#         article.text = request.form['text']
#         article.edit_date = datetime.now(TIMEZONE)
#         try:
#             db.session.commit()
#             return redirect('/posts')
#         except:
#             return 'При редактировании статьи возникла ошибка'
#     else:
#         return render_template('post_update.html', article=article, context=context)

#
# def updateUserAvatar(avatar, user_id):
#     user = User.query.get(user_id)
#     if not avatar:
#         return 'False1'
#     try:
#         user.avatar = avatar
#         db.session.commit()
#     except:
#         return 'False2'
#     return True


# @app.route('/userava')
# @login_required
# def userava(id=None):
#     if id:
#         user = User.query.get(id)
#         img = user.getAvatar()
#     else:
#         img = current_user.getAvatar(app)
#     if not img:
#         return ""
#     h = make_response(img)
#     h.headers['Content-Type'] = 'image/png'
#     return h

# @app.route('/upload', methods=["POST", "GET"])
# @login_required
# def upload():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and current_user.verifyExt(file.filename):
#             try:
#                 img = file.read()
#                 res = updateUserAvatar(img, current_user.get_id())
#                 if not res:
#                     flash("Ошибка обновления аватара", "error")
#                     return redirect(url_for('profile'))
#                 flash("Аватар обновлен", "success")
#             except FileNotFoundError as e:
#                 flash("Ошибка чтения файла", "error")
#         else:
#             flash("Ошибка обновления аватара", "error")
#
#     return redirect(url_for('profile'))


# @app.route('/profile/edit', methods=["POST", "GET"])
# @login_required
# def profile_edit():
#     context = {'user_is_authenticated': current_user.is_authenticated, 'legend': f'Профиль {current_user.login}'}
#
#     form = UserEditForm()
#     if form.validate_on_submit():
#         picture_name = save_image(form.avatar.data)
#         current_user.picture_name = picture_name
#         db.session.commit()
#         return redirect(url_for('profile'))
#
#     picture_url = url_for('static', filename='profile_pics/'+current_user.picture_name)
#
#     return render_template('profile_edit.html', context=context, form=form, image_url=picture_url)


# @app.route('/profile', methods=["POST", "GET"])
# @login_required
# def profile():
#     context = {'user_is_authenticated': current_user.is_authenticated, 'legend': f'Профиль {current_user.login}'}
#
#     form = UserEditForm()
#     if form.validate_on_submit():
#         picture_name = save_image(form.avatar.data)
#         current_user.picture_name = picture_name
#         db.session.commit()
#         return redirect(url_for('profile'))
#
#     picture_url = url_for('static', filename='profile_pics/'+current_user.picture_name)
#
#     return render_template('profile.html', context=context, form=form, image_url=picture_url)