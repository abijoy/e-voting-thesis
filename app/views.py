import datetime
import json

import requests
from flask import render_template, redirect, request
from flask import flash
from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_SERVICE_ADDRESS = "http://127.0.0.1:8000"
POLITICAL_PARTIES = ["Candidate A","Candidate B","Candidate C"]
VOTER_IDS=[
        'VOID001','VOID002','VOID003',
        'VOID004','VOID005','VOID006',
        'VOID007','VOID008','VOID009',
        'VOID010','VOID011','VOID012',
        'VOID013','VOID014','VOID015']

pub_key_v_ids = {

}

vote_check=[]

posts = []


def fetch_posts(voter_pub_key):
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_SERVICE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        vote_count = []
        chain = json.loads(response.content)
        is_voted = False
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                if tx["voter_id"] == voter_pub_key:
                    is_voted = True
                content.append(tx)



        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)
        
        print('------------ POSTS ------------')
        print(posts)
        
        return is_voted


from hashlib import sha256
def compute_hash(voter_id):
    """
    A function that return the hash of the block contents.
    """
    return sha256(voter_id.encode()).hexdigest()

# v_ids = []
from flask import url_for
@app.route('/', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        voter_nid = request.form["voter_nid"]
        voter_fullname = request.form["voter_fullname"]
        voter_dob = request.form["voter_dob"]

        # here call GOVT VOTER DATABASE TO VERIFY VOTER IDENTITY
        print(voter_nid, voter_fullname, voter_dob)
        voter_details = {
            'fullname': voter_fullname,
            'dob': voter_dob,
            'nid': voter_nid
        }
        govt_db_addr = 'http://127.0.0.1:9000/verify'
        resp = requests.get(govt_db_addr,
                    json=voter_details,
                    headers={'Content-type': 'application/json'})
        voter_pub_key = sha256(json.dumps(voter_details, sort_keys=True).encode('utf-8')).hexdigest()
        print(voter_pub_key)

        resp = json.loads(resp.content.decode())
        print(f"STATUS: {resp['status']}")
        
        pub_key_v_ids[voter_pub_key] = resp['status']
        print(pub_key_v_ids)
        if resp['status']:
            flash('Congratulations! You are an eligible Voter.')
            
            return redirect(f'/voting-ui/{voter_pub_key}')
        else:
            flash('Sorry! You are not eligible to vote', 'error')
            return redirect('/')
    else:
        auth_process_img = url_for('static', filename='authentication-govt.drawio.png')
        return render_template('verify.html', auth_process_img_url=auth_process_img)


@app.route('/voting-ui/<string:voter_pub_key>')
def index(voter_pub_key):
    is_voted = fetch_posts(voter_pub_key)
    print('--------------IS VOTED: ', is_voted)
    vote_gain = []

    for post in posts:
        vote_gain.append(post["party"])

    global v_ids
    v_ids = list(map(lambda x: compute_hash(x), VOTER_IDS))
    blockchain_img = url_for('static', filename='blockchain.png')
    return render_template('index.html',
                           title='E-voting system '
                                 'using Blockchain and python',
                           posts=posts,
                           vote_gain=vote_gain,
                           node_address=CONNECTED_SERVICE_ADDRESS,
                           readable_time=timestamp_to_string,
                           political_parties=POLITICAL_PARTIES,
                           voter_ids=VOTER_IDS,
                           voter_pub_key=voter_pub_key,
                           blockchain_img=blockchain_img,
                           is_voted = str(is_voted),
                           root='False'
                           )


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    party = request.form["party"]
    voter_id = request.form["voter_id"]
    print(voter_id)
    TxID = compute_hash(voter_id + party)

    post_object = {
        'voter_id': voter_id,
        'party': party,
        'TxID': TxID
    }
    print(f'Post object:::::: {post_object}')
    print(f'Public Keys::::: {pub_key_v_ids}')
    if voter_id not in pub_key_v_ids:
        flash('Something Went Wrong!', 'error')
        return redirect(f'/voting-ui/{voter_id}')
    if voter_id in vote_check:
        flash('You ('+voter_id+') have already voted!', 'error')
        flash('Please wait for a moment! Your Vote is being validated.', 'success')
        return redirect(f'/voting-ui/{voter_id}')
    else:
        vote_check.append(voter_id)
    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_SERVICE_ADDRESS)

    resp = requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    print(f'TRANSACTION STATUS: {resp.status_code}, {type(resp.status_code)}')
    if resp.status_code == 200:
        # print(vote_check)
        flash('Voted to '+party+' successfully!', 'success')
        flash('Your Vote is Waiting to be confirmed by the Proof-of-Authority Nodes.', 'success')
    if resp.status_code == 404:
        flash('You cannot vote multiple times!', 'error')
    return redirect(f'/voting-ui/{voter_id}')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
