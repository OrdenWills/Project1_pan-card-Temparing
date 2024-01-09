import cv2
import os
from skimage.metrics import structural_similarity
from PIL import Image
from flask import Flask,render_template,redirect,url_for,request,flash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e8yrh0fd9j8yd8hfi0a;kmipsdjhiw'

IMG_DIR = './static/images'

@app.route('/',methods=['POST','GET'])
def index():
    error = None
    if request.method == 'POST':
        print([i for i in request.files])
        if 'picture' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['picture']
        if file.filename == '':
            error = 'No selected file'
            return redirect(url_for('index',error=error))
                
        user_card = request.files['picture']
        user_card.save('./static/images/pan_card.png')
        return redirect(url_for('validate'))
    return render_template('index.html')

@app.route('/validate')
def validate():
    """Compare the original image to the uploaded and validates it to confirm they are similar"""
    status = None
    original_image = Image.open('./static/images/original.png')
    tempered = Image.open('./static/images/pan_card.png')
    # checks to confirm uploaded image has the same size as the original image
    if original_image.size != tempered.size:
        tempered = tempered.resize(original_image.size)
    # checks to validate the uploaded image and the origianl has the same format
    if original_image.format != tempered.format:
        tempered = tempered.save('{}/tempered.png'.format(IMG_DIR))

    # Load the images
    original = cv2.imread(f'{IMG_DIR}/original.png')
    tempered = cv2.imread(f'{IMG_DIR}/pan_card.png')

    # Convert the images to grayscale
    original_gray = cv2.cvtColor(original,cv2.COLOR_BGR2GRAY)
    tampered_gray = cv2.cvtColor(tempered,cv2.COLOR_BGR2GRAY)

    # Compute the structural similarity index (ssim)
    score,diff = structural_similarity(original_gray,tampered_gray,full=True)
    if round((score * 100)) < 60:
        stat = 'Fake'
    else:
        stat = 'validated you can proceed now!'
    return redirect(url_for('status',stat=stat))

@app.route('/validate/<stat>:')
def status(stat):
    return render_template('success.html',stat=stat)
if __name__ == '__main__':
    app.run(debug=True)