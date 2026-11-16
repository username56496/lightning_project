from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 가상의 메모리 DB
meetings = [
    {"id": 1, "title": "오늘 밤 한강 러닝 3명 구함!", "max_people": 3, "password": "1234", "members": ["김철수", "이영희"]}
]

# 1. 모임 목록 조회 및 생성
@app.route('/meetings', methods=['GET', 'POST'])
def handle_meetings():
    if request.method == 'GET':
        safe_meetings = [{k: v for k, v in m.items() if k != 'password'} for m in meetings]
        return jsonify({"status": "success", "data": safe_meetings})
    
    data = request.json
    title = data.get('title')
    max_people = int(data.get('max_people', 3))
    password = data.get('password')
    
    if not title:
        return jsonify({"status": "fail", "message": "모임 제목을 입력해주세요!"}), 400
    if not password:
        return jsonify({"status": "fail", "message": "삭제 및 수정용 비밀번호를 입력해주세요!"}), 400
    
    new_meeting = {
        "id": len(meetings) + 1 if not meetings else max(m["id"] for m in meetings) + 1,
        "title": title,
        "max_people": max_people,
        "password": password,
        "members": []
    }
    meetings.append(new_meeting)
    return jsonify({"status": "success", "message": "모임이 개설되었습니다!", "data": {k: v for k, v in new_meeting.items() if k != 'password'}})

# 2. 선착순 참여 신청
@app.route('/meetings/<int:meeting_id>/join', methods=['POST'])
def join_meeting(meeting_id):
    data = request.json
    nickname = data.get('nickname', '익명')
    
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    
    if not meeting:
        return jsonify({"status": "fail", "message": "존재하지 않는 모임입니다."}), 404
        
    if not nickname:
        return jsonify({"status": "fail", "message": "닉네임을 입력해야 합니다."}), 400
        
    if len(meeting["members"]) >= meeting["max_people"]:
        return jsonify({"status": "fail", "message": "이미 정원이 마감된 모임입니다!"}), 400
        
    if nickname in meeting["members"]:
        return jsonify({"status": "fail", "message": "이미 참여한 닉네임입니다."}), 400

    meeting["members"].append(nickname)
    return jsonify({"status": "success", "message": f"'{nickname}'님 참여 완료!"})

# 3. 모임 수정 기능 (비밀번호 검증 추가)
@app.route('/meetings/<int:meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    data = request.json or {}
    input_password = data.get('password')
    new_title = data.get('title')
    new_max_people = data.get('max_people')
    
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    
    if not meeting:
        return jsonify({"status": "fail", "message": "존재하지 않는 모임입니다."}), 404
        
    # 비밀번호 검증
    if meeting["password"] != input_password:
        return jsonify({"status": "fail", "message": "비밀번호가 틀렸습니다! 수정할 수 없습니다."}), 403
        
    # 현재 참여 중인 인원수보다 정원을 낮게 설정하는 것 방지
    if new_max_people is not None:
        new_max_people = int(new_max_people)
        if new_max_people < len(meeting["members"]):
            return jsonify({"status": "fail", "message": f"현재 참여 중인 인원({len(meeting['members'])}명)보다 정원을 낮출 수 없습니다!"}), 400
        meeting["max_people"] = new_max_people
        
    if new_title:
        meeting["title"] = new_title
        
    return jsonify({"status": "success", "message": "모임이 성공적으로 수정되었습니다!"})

# 4. 모임 삭제 (비밀번호 검증)
@app.route('/meetings/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    global meetings
    data = request.json or {}
    input_password = data.get('password')
    
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    
    if not meeting:
        return jsonify({"status": "fail", "message": "존재하지 않는 모임입니다."}), 404
        
    if meeting["password"] != input_password:
        return jsonify({"status": "fail", "message": "비밀번호가 틀렸습니다! 삭제할 수 없습니다."}), 403
        
    meetings = [m for m in meetings if m["id"] != meeting_id]
    return jsonify({"status": "success", "message": "모임이 안전하게 삭제되었습니다!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)