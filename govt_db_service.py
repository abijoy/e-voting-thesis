from flask import Flask, request, jsonify

app = Flask(__name__)

# Voter Governement Database.
voters_data = {
    '1234567892':{
        'full_name': 'Md. Al Amin',
        'dob': '1999-04-02',
        'eligible': True,
        'voted': False
    },

    '1234567893':{
        'full_name': 'Karim Islam',
        'dob': '1999-04-03',
        'eligible': True,
        'voted': False
    },

    '1234567894':{
        'full_name': 'Rahim Islam',
        'dob': '1999-04-04',
        'eligible': True,
        'voted': False
    },

    '1234567895':{
        'full_name': 'Salam Islam',
        'dob': '1999-04-05',
        'eligible': False,
        'voted': False
    },
}



# @app.route('/verify', methods=['GET'])
# def verify():
#     pass


@app.route('/verify', methods=['GET'])
def verify():
    voter_details = request.get_json()
    
    print('----- VOTER DETAILS ----')
    nid = voter_details['nid']
    print(nid)
    if nid in voters_data.keys():
        voter = voters_data[nid]
        print(voter['eligible'])
        if all((voter['full_name'] == voter_details['fullname'], voter['dob'] == voter_details['dob'], voter['eligible'] == True)):
            return jsonify({'status': True})
        else:
            return {'status': False}
    else:
        return {'status': False} 


if __name__ == '__main__':
    app.run(debug=True)
