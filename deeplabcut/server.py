'''
DeepLabCut Server
Jordan Salvi

Server wrapper for DeepLabCut (deeplabcut.org)

Licensed under GNU Lesser General Public License v3.0
'''

import os
import random
import pymongo
import deeplabcut
from flask import Flask, Blueprint, send_file
from flask import request
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

dlc = Blueprint('dlc', __name__)
dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbclient["deeplabcut"]
projectRepository = db["projects"]

@dlc.route('/')
def default():
    return "DeepLabCut Server Running"

#TODO: Important: Add file validation here
@dlc.route('/<projectId>/video_upload', methods=['POST'])
def video_upload(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    if 'file' not in request.files:
        return "No file was sent"
    project_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path'][0:-11] + 'videos/'
    file = request.files['file']
    filename = secure_filename(file.filename)
    video_path = os.path.join(project_path, filename)
    file.save(video_path)
    deeplabcut.add_new_videos(config_path, [video_path])
    return "Video uploaded"  #TODO: Return real response

@dlc.route('/create', methods=['POST'])
def create():
    name = request.json['project_name']
    experimenter = request.json['experimenter']
    config_path = deeplabcut.create_new_project(name,experimenter,[])
    projectId = projectRepository.insert_one({'project_name': name, 'experimenter': experimenter, 'config_path': config_path}).inserted_id
    return "Project " + str(projectId) + " created."  #TODO: Return real response

'''
example request = { 
    "algo":"kmeans", 
    "crop":"False",  
    "cluster_step":1,
    "cluster_resizewidth":30, 
    "cluster_color":"false", 
    "opencv":"true", 
    "slider_width":25
}
'''
@dlc.route('/<projectId>/extract_frames', methods=['POST'])
def extract_frames(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    if (request.is_json):
        deeplabcut.extract_frames(config_path, 
                                'automatic', 
                                request.json['algo'],
                                request.json['crop'],
                                False,
                                request.json['cluster_step'],
                                request.json['cluster_resizewidth'],
                                request.json['cluster_color'],
                                request.json['opencv'],
                                request.json['slider_width'],
                                True)
    else:
        deeplabcut.extract_frames(config_path, "automatic", "kmeans", False, False, 1, 30, False, True, 25, True)
    return "Done" 

# return a single frame for annotation
@dlc.route('/<projectId>/get_frame', methods=['GET'])
def get_frame(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    video_paths = config_path[:-11] + "labeled-data"
    frame_files = []
    for p in os.listdir(video_paths):
        if not (p[0] == '.'):
            for f in os.listdir(video_paths + '/' + p):
                frame_files.append(video_paths + '/' + p + '/' + f)
    img = frame_files[random.randint(0,len(frame_files)-1)]
    return send_file(img)
                                
@dlc.route('/<projectId>/label_frames', methods=['POST'])
def label_frames(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    #TODO: cannot use the dlc label_frames method because it is gui based
    print("test")
    deeplabcut.label_frames(config_path) 
    return "Not Implemented", 501

@dlc.route('/<projectId>/check_labels', methods=['GET'])
def check_labels(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    err_folders = deeplabcut.check_labels(config_path)
    if (len(err_folders) > 0):
        return "Some labels were incorrect", 400
    else: 
        return "OK", 200

@dlc.route('/<projectId>/create_training_dataset', methods=['GET'])
def create_training_dataset(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    #deeplabcut.create_training_dataset(config_path)
    return "Not Implemented", 501

@dlc.route('/<projectId>/train_network', methods=['GET'])
def train_network(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    #deeplabcut.train_network(config_path)
    return "Not Implemented", 501

@dlc.route('/<projectId>/evaluate_network', methods=['GET'])
def evaluate_network(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    #deeplabcut.evaluate_network(config_path)
    return "Not Implemented", 501
    
#TODO: route - get trained model can be done later
@dlc.route('/<projectId>/get_trained_model', methods=['GET'])
def get_trained_model(projectId):
    return "Not Implemented", 501

@dlc.route('/<projectId>/analyze_videos', methods=['POST'])
def analyze_videos(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    deeplabcut.analyze_videos(config_path, [])
    return "Not Implemented", 501

@dlc.route('/<projectId>/filterpredictions', methods=['POST'])
def filterpredictions(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    deeplabcut.filterpredictions(config_path, [])
    return "Not Implemented", 501

@dlc.route('/<projectId>/plot_trajectories', methods=['POST'])
def plot_trajectories(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    deeplabcut.plot_trajectories(config_path, [], filtered=True)
    return "Not Implemented", 501

@dlc.route('/<projectId>/create_labeled_video', methods=['POST'])
def create_labeled_video(projectId):
    config_path = projectRepository.find_one({'_id': ObjectId(projectId)})['config_path']
    deeplabcut.create_labeled_video(config_path, [], filtered=True)
    return "Not Implemented", 501

if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(dlc, url_prefix='/')
    app.wsgi_app = ProxyFix(app.wsgi_app)
    print(app.url_map)
    app.run()