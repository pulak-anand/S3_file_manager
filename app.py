from flask import Flask, render_template, request, redirect, url_for, flash, Response, session
from flask_bootstrap import Bootstrap
from filters import datetimeformat, file_type
from resources import get_bucket, get_buckets_list, create_folder,delete_folder,rename_file,copy_to_bucket
import functools


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            username = session['username']
        except KeyError:
            session['username'] = None
        if session['username'] is None:
            return redirect('login')
        return view(**kwargs)

    return wrapped_view

@app.route('/',methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
        buckets = get_buckets_list()
        return render_template("index.html", buckets=buckets)

@app.route('/files', methods = ['GET','POST'])
@login_required
def files():
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()
    print("my_bucket", my_bucket)
    print("summaries", summaries)
    return render_template('files.html', my_bucket=my_bucket, files=summaries)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('files'))

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))

@app.route('/download', methods=['POST'])
@login_required
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

@app.route('/rename', methods=['POST'])
@login_required
def rename():            
    old_name = request.form['old_name']
    folder_name = request.form['folder_name']
    new_name = folder_name +"/"+ request.form['new_name']
    
    bucket_name = str(request.form['bucket_name'])
    rename_file(bucket_name,folder_name,new_name,old_name)
    return redirect(url_for('files', bucket_name= bucket_name,folder_name = folder_name))

@app.route('/copy', methods=['POST'])
@login_required
def copyfile():       
    source_bucket = str(request.form['source_bucket'])
    folder_name = request.form['folder_name']
    source_key = request.form['source_key']
    other_bucket = request.form['other_bucket']
    otherkey = request.form['other_folder'] +"/" + request.form['otherkey']

    copy_to_bucket(source_bucket,source_key,other_bucket,otherkey)
    return redirect(url_for('files', bucket_name= source_bucket,folder_name = folder_name))

@app.route('/createfolder', methods=['POST'])
@login_required
def createfolder():       
    bucket_name = str(request.form['bucket_name'])
    folder_name = request.form['folder_name'] + "/"
    create_folder(bucket_name,folder_name)
    return redirect(url_for('folders', bucket_name=bucket_name))

@app.route('/deletefolder', methods=['POST'])
@login_required
def deletefolder():       
    bucket_name = str(request.form['bucket_name'])
    folder_name = request.form['folder_name']
    delete_folder(bucket_name,folder_name)
    return redirect(url_for('folders', bucket_name=bucket_name))

@app.route('/movefile', methods=['POST'])
@login_required
def movefile():       
    source_bucket = str(request.form['source_bucket'])
    folder_name = request.form['folder_name']
    source_key = request.form['source_key']
    other_bucket = request.form['other_bucket']
    otherkey = request.form['otherkey']
    copy_to_bucket(source_bucket,source_key,other_bucket,otherkey)
    delete(source_bucket,source_key)
    return redirect(url_for('files', bucket_name= source_bucket,folder_name = folder_name))

@app.route('/login', methods=('GET', 'POST'))
def login():
    session['username'] = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if username != "pulak":
            error = 'Incorrect username.'
        elif password != "12341234":
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['username'] = username
            return redirect('/')
    return render_template('login.html')

if __name__=="__main__":
    app.run(debug=True)