from flask import Flask,render_template,flash,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

# 编码
# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

app = Flask(__name__)


# 1、配置数据库
#     a、导入SQLAlchemy扩展
#     b、创建db对象，并配置参数
#     c、终端创建数据库

# 2、添加书和作者的模型
#     a、模型继承db.Model
#     b、__tablename__:表名
#     c、db.Column:字段
#     d、db.relationship:关系引用

# 3、添加数据

# 4、使用模板显示数据
#     a、查询所有的作者信息，让信息传递给模板
#     b、模板中按照格式，依次for循环作者和书籍即可

# 5、使用WTF显示表单
#     a、自定义表单类
#     b、模板中显示
#     c、secret_key / 编码 / csrf_token

# 6、实现相关的增删逻辑
#     a、增加数据
#     b、删除书籍  url_for的使用 / for_else的使用 / redirect使用
#     c、删除作者

# 1、数据库配置：数据库地址/关闭自动跟踪

    # 数据库类型://用户名:密码@主机地址:端口号/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/book'
    # 跟踪数据库修改，不建议开启，设置为False，后续版本将会删除此属性
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'abc'

    #   创建数据库对象的时候需要传入app
db=SQLAlchemy(app)

# 2、定义书和作者模型
    # 作者模型
class Author(db.Model):
    # 表名
    __tablename__ = 'authors'
    # 字段
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(16),unique=True)
    # 关系引用
    # books是给自己（Author模型）用的，author是给Book模型建的
    books=db.relationship('Book',backref='author')

    def __repr__(self):
        return 'Author: %s ' % self.name

    # 书籍模型
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer,primary_key=True)
    name =db.Column(db.String(16),unique=True)
    author_id = db.Column(db.Integer,db.ForeignKey('authors.id'))

    def __repr__(self):
        return 'Book: %s %s' % (self.name,self.author_id)


# 5、使用WTF显示表单
    # 自定义表单类
class AuthorForm(FlaskForm):
    author = StringField('作者：',validators=[DataRequired()])
    book = StringField('书籍：',validators=[DataRequired()])
    submit = SubmitField('提交')




# 6、b、删除书籍 -->网页中删除 --> 点击需要发送书籍的ID给删除书籍的路由 -->路由需要接收参数
@app.route('/delete_book/<book_id>')
def delete_book(book_id):

    # 1、查询数据库是否有该id的书，
    book = Book.query.get(book_id)

    # 2、有就删除
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍出错')
            db.session.rollback()
    else:
        # 3、没有就提示错误
        flash('书籍找不到')

    # 如何返回当前网址 -->重定向(redirect  需要传入网络/路由地址)
    # return redirect('www.baidu.com')
    # url_for('index'):需要传入视图函数名，返回该视图函数对应的路由地址
    return redirect(url_for('index'))


# 6、c、删除作者
@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    # 查询数据库，是否有该id的作者，如果有就删除（先删书，再删作者），没有就提示
    # 1、查询数据库
    author = Author.query.get(author_id)
    # 2、如果有就删除（先删书，再删作者）
    if author:
        try:
            Book.query.filter_by(author_id=author.id).delete()
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者出错')
            db.session.rollback()
    else:
        # 3、没有就提示错误
        flash('作者找不到')


    return redirect(url_for('index'))



@app.route('/',methods=['GET','POST'])
def index():

# 5、创建自定义表单类
    author_form = AuthorForm()

# 6、a、1、调用WTF的函数实现验证
    #     2、验证通过获取数据
    #     3、判断作者是否存在
    #     4、如果作者存在，判断书籍是否存在，没有重复就添加数据，如果重复就提示
    #     5、如果作者不存在就添加作者和书籍
    #     6、验证不通过就提示错误

    # 1、调用WTF的函数实现验证
    if author_form.validate_on_submit():
        # 2、验证通过获取数据
        author_name = author_form.author.data
        book_name = author_form.book.data

        # 3、判断作者是否存在
        author = Author.query.filter_by(name=author_name).first()

        # 4、如果作者存在
        if author:
            # 判断书籍是否存在，
            book = Book.query.filter_by(name=book_name).first()
            # 如果重复就提示
            if book:
                flash('已存在')
            # 没有重复就添加数据
            else:
                try:
                    new_book = Book(name=book_name,author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print (e)
                    flash('添加书籍失败')
                    db.session.rollback()

        else:
            # 5、如果作者不存在就添加作者和书籍
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name,author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()

            except Exception as e:
                print (e)
                flash('添加作者和书籍失败')
                db.session.rollback()
    else:
        # 6、验证不通过就提示错误
        if request.method == 'POST':
             flash('参数不全')


# 4、使用模板显示数据
     # 查询所有的作者信息，把信息传递给模板
    authors = Author.query.all()


    return render_template('books.html',authors=authors,form=author_form)


if __name__ == '__main__':

# 3、添加数据

    db.drop_all()
    db.create_all()

    # 生成数据
    au1 = Author(name='老王')
    au2 = Author(name='老刘')
    au3 = Author(name='老李')
    # 把数据提交给用户会话
    db.session.add_all([au1,au2,au3])
    # 提交会话
    db.session.commit()
    bk1=Book(name='老王回忆录',author_id=au1.id)
    bk2=Book(name='好好好',author_id=au1.id)
    bk3=Book(name='都发给收的标准续保',author_id=au2.id)
    bk4=Book(name='热腾腾月',author_id=au2.id)
    bk5=Book(name='法规的风格',author_id=au3.id)
    bk6=Book(name='是场各环节过',author_id=au3.id)
    # 把数据提交给用户会话
    db.session.add_all([bk1,bk2,bk3,bk4,bk5,bk6])
    # 提交会话
    db.session.commit()


    app.run(debug=True)
