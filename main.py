import flask
from flask import request, render_template, send_file, url_for
from index import *
from flask import Flask, send_from_directory
from flask import json, jsonify
import json
import sqlite3
import pdfkit
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
type_profile_utop = """При утопленном профиле шкала Л обычно от 4 до 8 Сб.
Утопленный профиль всегда сопровождается повышением шкалы К. Это отражает закрытую позицию пациента. Обычно К от 60 до 70 Тб. 
Такой профиль не подлежит КЛИНИЧЕСКОЙ интерпретации, и можно рассматривать только оценочные шкалы ЛФК. При этом надо брать в расчет здоровый ли это человек, или ему поставлен официальный психиатрический (не психотический) диагноз.
У здорового человека – суперзакрытая позиция. И это здоровая реакция нормального человека (этакий изящный способ избежать открытости своего внутреннего мира).  
Если же клиент с диагнозом (и даже предварительным) психиатрического порядка (это уже измененная личность), то у таких людей утопленный профиль чаще всего отражает не суперзакрытую позицию, а отражает изменения в сторону снижения эмоциональных реакций. Обычно таким пациентам свойственны проблемы с критикой. 
Создатели теста видели, что есть серьезная корреляция между давностью заболевания и степенью утопленности профиля."""
type_profile_normat = """• От 45 до 65 Тб, часто линейный профиль.
• Профиль не подлежит клинической интерпретации, так как ничего не говорит о человеке.
• Сбалансированность тенденций, гармоничность личности, достаточная реалистичность, умение решать сложные задачи, высокая социальная адаптация. Чувства и поведение подчинены контролю сознания (эмоции настолько умеренны, что минимальный контроль над ними оказывается вполне достаточным).
• Если оценочные шкалы выявляют признаки искажения результатов, то при таком типе повышение по Л или К.
Тогда профиль рассматривается и интерпретируется как утопленный:

1. Проблемы контакта между пациентом и экспериментатором.

2. Ситуативно искажен (человек сознательно не хочет, чтобы лезли в его внутренний мир)."""
type_profile_kvazi = """• Повышение одной или нескольких шкал от 65 до 70 Тб.
• Характерен для нормальных (психически здоровых) людей, которые обладают индивидуальностью.
• Можно интерпретировать с точки зрения описания акцентуированных черт личности (патологии нет)."""
type_profile_pogran = """• Пики (одна или несколько шкал) от 70 до 75 Тб.
• Профиль недоступен для интерпретации.
• Пики интерпретируются как акцентуации, выраженность черт. Наличие патологии характера зависит от возраста испытуемого (чем старше , тем хуже) и наличия/отсутствия признаков нарушения социальной адаптации испытуемого."""
type_profile_diapazon = """• Могут быть западения до 40 Тб
• Пики шкал (обычно от 1 до 3) достигают 75 – 80 Тб.
• Интерпретируются как пограничный и требуется тщательное изучение социальной адаптации (социальная дезадаптация).
1. Может быть психопатические черты характера, 
2. Может быть состояние стресса при экстремальной ситуации, сложная жизненная ситуация, травмирующее психику событие.
3. Может быть невротическое расстройство,
4. Может быть физическое недомогание (заболевание)."""
type_profile_float = """• Большинство шкал (5 или более из 10) превышают 70 Тб.
• Профиль не интерпретируется.
• Можно сказать, что «все плохо» - плохая психологическая и социальная адаптация, крайне тяжелое эмоциональное состояние. Нарушены межличностные контакты, когнитивная и эмоциональная дезорганизация; исчерпаны адаптационные ресурсы."""
type_profile_upper = """• Все шкалы более 50 Тб"""
type_profile_upl = """ • Разброс между минимумом и максимумом до 21 Тб"""
app = Flask(__name__)


@app.route('/api/v1/user/add', methods=['POST'])
def registerUser():
    deleted, name, age, email, date, gender = list(request.json.values())
    conn = sqlite3.connect("kovesh.db")
    cur = conn.cursor()
    cur.execute(f"select id from users where email='{email}'")
    a = cur.fetchone()
    if (a):
        answer = {"data": {"id": a[0]}, "status": "error"}
    else:
        cur.execute(f"insert into users (name, age, email, date, gender, deleted) values ('{name}', '{age}'"
                    f", '{email}', '{date}', '{gender}', '{deleted}')")
        conn.commit()
        cur.execute("select last_insert_rowid() from users")
        last_id = cur.fetchone()
        id = last_id[0]
        answer = {"data": {"id": id}, "status": "success"}
    conn.close()
    return jsonify(answer)


@app.route('/api/v1/quiz/add', methods=['POST'])
def registerTest():
    conn = sqlite3.connect("kovesh.db")
    cur = conn.cursor()
    data = list(request.json.values())
    date = data[0]
    data_user = list(data[1].values())
    id_user = data_user[1]
    cur.execute(f"insert into test (id_user, date) values ('{id_user}', '{date}')")
    cur.execute("select last_insert_rowid() from test")
    last_id = cur.fetchone()
    id = last_id[0]
    conn.commit()
    answer = {"data": {"id": id}}
    conn.close()
    return jsonify(answer)


@app.route('/api/v1/asck/add', methods=['POST'])
def sendAsck():
    conn = sqlite3.connect("kovesh.db")
    cur = conn.cursor()
    data = list(request.json.values())
    test = list(data[4].values())
    test_id = test[0]
    #cur.execute(f"insert into test (id_user, date) values ('{1}', '{'12/12/21'}')")
    cur.execute(f"select quiz_{data[0]} from test where id='{test_id}'")
    quiz = cur.fetchone()
    print(quiz)
    if (quiz[0] != None):
        cur.execute(f"select attemp from attemps where id='{test_id}' and quiz='{data[0]}'")
        check = cur.fetchone()
        if (not check):
            cur.execute(f"insert into attemps (id, quiz, attemp) values ('{test_id}', '{data[0]}', '2')")
        else:
            cur.execute(f"UPDATE attemps set attemp='{1 + int(check[0])}' where id='{test_id}' and quiz='{data[0]}'")
        conn.commit()
    cur.execute(f"UPDATE test set quiz_{data[0]}='{data[2]}', time_{data[0]}='{data[3]}' where id='{test_id}'")
    conn.commit()
    conn.close()
    return jsonify({"data": "success"})


@app.route('/api/v1/result/public/<testId>', methods=['GET'])
def getResult(testId):
    conn = sqlite3.connect("kovesh.db")
    cur = conn.cursor()
    cur.execute(f"select id_user from test where id='{testId}'")
    id_user = cur.fetchone()
    id = id_user[0]
    pdfkit.from_url(f"http://localhost:5000/pdf_gener/{testId}", f"{id}_{testId}.pdf")
    return jsonify(f"{id}_{testId}.pdf")


@app.route('/result/<filename>', methods=['GET'])
def result(filename):
    return send_from_directory("/home/kiselperdit/PycharmProjects/koveshnikov", f"{filename}")


@app.route("/pdf_gener/<testId>", methods=['GET'])
def pdf_generation(testId):
    def concat(index, data):
        data_index = list()
        for i in index:
            data_index += [data[i - 1]]
        return data_index

    conn = sqlite3.connect("kovesh.db")
    cur = conn.cursor()
    cur.execute(f"select * from test where id='{testId}'")
    data = cur.fetchone()
    cur.execute(f"select quiz, attemp from attemps where id='{testId}'")
    attemps_querry = cur.fetchall()
    attemps = sum([int(i[1]) - 1 for i in attemps_querry])
    quiz_attemps = ' '.join([i[0] for i in attemps_querry])
    print(quiz_attemps)
    print(attemps)
    data_values = list(data[3::2])
    data_values = list(filter(None, data_values))
    data_values = list(map(int, data_values))
    data_values = [i for i in range(1, len(data_values) + 1)]
    data_time = list(data[4::2])
    data_time = list(filter(None, data_time))
    data_time = list(map(int, data_time))
    time_test = sum(data_time)
    middle_time_test = time_test / len(data_values)
    min_time_test = min(data_time)
    max_time_test = max(data_time)
    id_user = data[1]
    date_test = data[2]
    data = list(data[3::2])
    cur.execute(f"select gender from users where id='{id_user}'")
    gender = cur.fetchone()[0]
    Data_L = concat(Index_L, data)
    Data_F_y = concat(Index_F_y, data)
    Data_F_n = concat(Index_F_n, data)
    Data_K_y = concat(Index_K_y, data)
    Data_K_n = concat(Index_K_n, data)
    Data_1_y = concat(Index_1_y, data)
    Data_1_n = concat(Index_1_n, data)
    Data_2_y = concat(Index_2_y, data)
    Data_2_n = concat(Index_2_n, data)
    Data_3_y = concat(Index_3_y, data)
    Data_3_n = concat(Index_3_n, data)
    Data_4_y = concat(Index_4_y, data)
    Data_4_n = concat(Index_4_n, data)
    Data_5m_y = concat(Index_5m_y, data)
    Data_5m_n = concat(Index_5m_n, data)
    Data_5f_y = concat(Index_5f_y, data)
    Data_5f_n = concat(Index_5f_n, data)
    Data_6_y = concat(Index_6_y, data)
    Data_6_n = concat(Index_6_n, data)
    Data_7_y = concat(Index_7_y, data)
    Data_7_n = concat(Index_7_n, data)
    Data_8_y = concat(Index_8_y, data)
    Data_8_n = concat(Index_8_n, data)
    Data_9_y = concat(Index_9_y, data)
    Data_9_n = concat(Index_9_n, data)
    Data_0_y = concat(Index_0_y, data)
    Data_0_n = concat(Index_0_n, data)
    SB_L, SB_F, SB_K, SB_1, SB_2, SB_3, \
    SB_4, SB_5, SB_6, SB_7, SB_8, SB_9, SB_0 = int(), int(), int(), int(), int(), int(), int(), int(), int(), int(), int(), int(), int()

    def summa(Data, oper):
        SB = 0
        for i in Data:
            if i == str(oper):
                SB += 1
        return SB
    SB_L = summa(Data_L, 0)
    SB_F = summa(Data_F_y, 1) + summa(Data_F_n, 0)
    SB_K = summa(Data_K_y, 1) + summa(Data_K_n, 0)
    SB_1 = summa(Data_1_y, 1) + summa(Data_1_n, 0)
    SB_2 = summa(Data_2_y, 1) + summa(Data_2_n, 0)
    SB_3 = summa(Data_3_y, 1) + summa(Data_3_n, 0)
    SB_4 = summa(Data_4_y, 1) + summa(Data_4_n, 0)
    if (gender == 'male'):
        SB_5 = summa(Data_5m_y, 1) + summa(Data_5m_n, 0)
    else:
        SB_5 = summa(Data_5f_y, 1) + summa(Data_5f_n, 0)
    SB_6 = summa(Data_6_y, 1) + summa(Data_6_n, 0)
    SB_7 = summa(Data_7_y, 1) + summa(Data_7_n, 0)
    SB_8 = summa(Data_8_y, 1) + summa(Data_8_n, 0)
    SB_9 = summa(Data_9_y, 1) + summa(Data_9_n, 0)
    SB_0 = summa(Data_0_y, 1) + summa(Data_0_n, 0)
    kk_correct = [[0] * 4 for i in range(31)]
    for i in range(1, 31):
        kk_correct[i][1] = (int((i + 1) * 0.5))
        kk_correct[i][2] = (int((i + 1) * 0.4))
        kk_correct[i][3] = (int((i + 1) * 0.2))
    kk_correct[1][2] = 1
    kk_correct[3][2] = 2
    kk_correct[5][1] = 2
    kk_correct[12][3] = 3
    kk_correct[13][2] = 6
    kk_correct[17][1] = 8
    kk_correct[18][2] = 8
    kk_correct[23][1] = 11
    kk_correct[25][1] = 12
    kk_correct[28][3] = 5
    kk_correct[23][3] = 5
    kk_correct[18][3] = 4
    kk_correct[13][3] = 3
    kk_correct[8][3] = 2
    kk_correct[3][3] = 1
    SB_1 = SB_1 + kk_correct[SB_K][1]
    SB_4 = SB_4 + kk_correct[SB_K][2]
    SB_7 = SB_7 + SB_K
    SB_8 = SB_8 + SB_K
    SB_9 = SB_9 + kk_correct[SB_K][3]
    #SB_L = 4
    #SB_F = 7
    #SB_K = 15
    #SB_1 = 10
    #SB_2 = 20
    #SB_3 = 19
    #SB_4 = 24
    #SB_5 = 39
    #SB_6 = 12
    #SB_7 = 35
    #SB_8 = 32
    #SB_9 = 25
    #SB_0 = 16
    if gender == 'male':
        TB_L = round(30.9004 + SB_L * 4.7692)
        TB_F = round(30.9992 + SB_F * 3.4063)
        TB_K = round(8.9 + SB_K * 2.62)
        TB_1 = round(15.092 + SB_1 * 2.9688)
        TB_2 = round(1.9 + SB_2 * 2.4)
        TB_3 = round(7.8664 + SB_3 * 2.3132)
        TB_4 = round(-0.5 + SB_4 * 2.39)
        TB_5 = round(-17.916 + SB_5 * 3.0704)
        TB_6 = round(16.3875 + SB_6 * 3.6045)
        TB_7 = round(-8.332 + SB_7 * 2.1222)
        TB_8 = round(-9.2519 + SB_8 * 2.2167)
        TB_9 = round(4.787 + SB_9 * 2.4714)
        TB_0 = round(10.7659 + SB_0 * 1.4481)
    else:
        TB_L = round(31.1 + SB_L * 4.25)
        TB_F = round(29 + SB_F * 3.08)
        TB_K = round(15.22 + SB_K * 2.376)
        TB_1 = round(18.125 + SB_1 * 2.175)
        TB_2 = round(2 + SB_2 * 2)
        TB_3 = round(10.758 + SB_3 * 1.9044)
        TB_4 = round(-1.775 + SB_4 * 2.3775)
        TB_5 = round(132.54 + SB_5 * -2.576)
        TB_6 = round(18.8 + SB_6 * 2.94)
        TB_7 = round(-17.75 + SB_7 * 2.1125)
        TB_8 = round(-5.334 + SB_8 * 1.8889)
        TB_9 = round(0.713 + SB_9 * 2.6286)
        TB_0 = round(9.96 + SB_0 * 1.284)
    cur.execute(f"select * from users where id='{id_user}'")
    information_user = cur.fetchone()
    conn.close()
    if gender == "male":
        gender = "М"
    else:
        gender = "Ж"
    labels = ["L", "F", "K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    values = [TB_L, TB_F, TB_K, TB_1, TB_2, TB_3, TB_4, TB_5, TB_6, TB_7, TB_8, TB_9, TB_0]
    plt.plot(labels, values, lw=3, color="blue", alpha=0.5)
    plt.scatter(labels, values, color='blue', s=10)
    plt.annotate(TB_L, xy=("L", TB_L + 3))
    plt.annotate(TB_F, xy=("F", TB_F + 3))
    plt.annotate(TB_K, xy=("K", TB_K + 3))
    plt.annotate(TB_1, xy=("1", TB_1 + 3))
    plt.annotate(TB_2, xy=("2", TB_2 + 3))
    plt.annotate(TB_3, xy=("3", TB_3 + 3))
    plt.annotate(TB_4, xy=("4", TB_4 + 3))
    plt.annotate(TB_5, xy=("5", TB_5 + 3))
    plt.annotate(TB_6, xy=("6", TB_6 + 3))
    plt.annotate(TB_7, xy=("7", TB_7 + 3))
    plt.annotate(TB_8, xy=("8", TB_8 + 3))
    plt.annotate(TB_9, xy=("9", TB_9 + 3))
    plt.annotate(TB_0, xy=("0", TB_0 + 3))
    plt.savefig(os.path.abspath(os.getcwd()) + f"/static/{id_user}_{testId}.png")
    plt.close()
    plt.plot(data_values, data_time, lw=2, color="blue", alpha=0.5)
    plt.scatter(data_values, data_time, color='blue', s=10)
    plt.savefig(os.path.abspath(os.getcwd()) + f"/static/{id_user}_{testId}_time.png")
    plt.close()
    img_root = f"{id_user}_{testId}.png"
    img_root_time = f"{id_user}_{testId}_time.png"
    date_one = information_user[2]
    year = datetime.datetime.strptime(str(date_one), "%Y")
    year_now = datetime.datetime.now()
    age = round((year_now - year).days / 365)
    index_welsh = SB_F - SB_K
    rating_veracity = str()
    androgyny = str()
    type_profile = str()
    type_profile_info = str()
    profile_tilt = str()
    if gender == "М":
        if index_welsh >= -18 and index_welsh <= 4:
            rating_veracity = "Хорошая достоверность"
        elif index_welsh == -7:
            rating_veracity = "Простая достоверность"
        elif index_welsh >= 5 and index_welsh <= 7:
            rating_veracity = "Сомнительная достоверность"
        elif index_welsh < -18 or index_welsh > 7:
            rating_veracity = "Профиль не достоверный(требуются иные методики диагностики)"
    else:
        if index_welsh >= -23 and index_welsh <= 7:
            rating_veracity = "Хорошая достоверность"
        elif index_welsh == 8:
            rating_veracity = "Простая достоверность"
        elif index_welsh > 8 and index_welsh <= 10:
            rating_veracity = "Сомнительная достоверность"
        elif index_welsh < -23 or index_welsh > 10:
            rating_veracity = "Профиль не достоверный(требуются иные методики диагностики)"
    if gender == "М":
        if TB_5 > 54 and TB_5 < 66:
            androgyny = "Норма"
        elif TB_5 > 65:
            androgyny = "Доминирование женского типа поведения"
        elif TB_5 < 55:
            androgyny = "Доминирование мужского типа поведения"
    else:
        if TB_5 > 54 and TB_5 < 66:
            androgyny = "Норма"
        elif TB_5 > 65:
            androgyny = "Доминирование мужского типа поведения"
        elif TB_5 < 55:
            androgyny = "Доминирование женского типа поведения"
    SAP = (TB_4 + TB_6 + TB_8 + TB_9) / 4
    SAN = (TB_1 + TB_2 + TB_3) / 3
    if (abs(SAP - SAN) < 1 and abs(SAP - SAN) > 0):
        profile_tilt = "Нулевой"
    elif (SAP < SAN):
        profile_tilt = "Невротический"
    elif (SAN < SAP):
        profile_tilt = "Психотический"
    rating_profile = ["""1"""]
    analytics = [TB_F, TB_L, TB_K, TB_1, TB_2, TB_3, TB_4, TB_5, TB_6, TB_7, TB_8, TB_9, TB_0]
    code_welsh = str()
    analytics_clinical_dict = {"1":TB_1, "2":TB_2, "3":TB_3,
                               "4":TB_4, "5":TB_5, "6":TB_6, "7":TB_7, "8":TB_8, "9":TB_9, "0":TB_0}
    analytics_clinical_sort = list(analytics_clinical_dict.items())
    analytics_clinical_sort.sort(key= lambda i: i[1], reverse=True)
    analytics_notes_dict = {"F":TB_F, "K":TB_K, "L":TB_L}
    analytics_notes_sort = list(analytics_notes_dict.items())
    analytics_notes_sort.sort(key= lambda i: i[1], reverse=True)
    code_welsh = ""
    char = ["", "", "", "", "", "", "", "", "", "", ""]
    for i in analytics_clinical_sort:
        if int(i[1]) > 120:
            char[0] += i[0]
        elif int(i[1]) > 110:
            char[1] += i[0]
        elif int(i[1]) > 100:
            char[2] += i[0]
        elif int(i[1]) > 90:
            char[3] += i[0]
        elif int(i[1]) > 80:
            char[4] += i[0]
        elif int(i[1]) > 70:
            char[5] += i[0]
        elif int(i[1]) > 60:
            char[6] += i[0]
        elif int(i[1]) > 50:
            char[7] += i[0]
        elif int(i[1]) > 40:
            char[8] += i[0]
        elif int(i[1]) > 30:
            char[9] += i[0]
        else:
            char[10] += i[0]
    if (char[0]):
        char[0] += "!!"
    if (char[1]):
        char[1] += "!"
    if (char[2]):
        char[2] += "**"
    if (char[3]):
        char[3]+= "*"
    if (char[4]):
        char[4] += '"'
    if (char[5]):
        char[5] += "'"
    if (char[6]):
        char[6] += "-"
    if (char[7]):
        char[7] += "/"
    if (char[8]):
        char[8] += ":"
    if (char[9]):
        char[9] += "#"
    for i in char:
        code_welsh += i
    code_welsh += ""
    char = ["", "", "", "", "", "", "", "", "", "", ""]
    for i in analytics_notes_sort:
        if int(i[1]) > 120:
            char[0] += i[0]
        elif int(i[1]) > 110:
            char[1] += i[0]
        elif int(i[1]) > 100:
            char[2] += i[0]
        elif int(i[1]) > 90:
            char[3] += i[0]
        elif int(i[1]) > 80:
            char[4] += i[0]
        elif int(i[1]) > 70:
            char[5] += i[0]
        elif int(i[1]) > 60:
            char[6] += i[0]
        elif int(i[1]) > 50:
            char[7] += i[0]
        elif int(i[1]) > 40:
            char[8] += i[0]
        elif int(i[1]) > 30:
            char[9] += i[0]
        else:
            char[10] += i[0]
    if (char[0]):
        char[0] += "!!"
    if (char[1]):
        char[1] += "!"
    if (char[2]):
        char[2] += "**"
    if (char[3]):
        char[3]+= "*"
    if (char[4]):
        char[4] += '"'
    if (char[5]):
        char[5] += "'"
    if (char[6]):
        char[6] += "-"
    if (char[7]):
        char[7] += "/"
    if (char[8]):
        char[8] += ":"
    if (char[9]):
        char[9] += "#"
    for i in char:
        code_welsh += i
    an = 0
    for i in analytics:
        if (i > 60):
            an = 0
            break
        elif (i < 50):
            an += 1
    if (an >= 5):
        type_profile = "Утопленный"
        type_profile_info = type_profile_utop
    an = 0
    for i in analytics:
        if (i >= 45 and i < 65):
            an += 1
        else:
            an = 0
            break
    if (an == 13):
        type_profile = "Нормативный"
        type_profile_info = type_profile_normat
    an = 0
    for i in analytics:
        if (i >= 65 and i < 70):
            type_profile = "Квазинормативный"
            type_profile_info = type_profile_kvazi
            break
    for i in analytics:
        if (i >= 70 and i < 75):
            type_profile = "Пограничный"
            type_profile_info = type_profile_pogran
            break
    for i in analytics:
        if (i >= 75 and i < 80):
            an += 1
    if (an > 0 and an < 4):
        type_profile = "Высокодиапазонный"
        type_profile_info = type_profile_diapazon
    an = 0
    for i in analytics:
        if (i > 70):
            an += 1
    if (an >= 5):
        type_profile = "Плавающий"
        type_profile_info = type_profile_float
    an = 0
    for i in analytics:
        if (i > 50):
            an += 1
    if (an == 13):
        type_profile = "Приподнятый"
        type_profile_info = type_profile_upper
    an = 0
    if (max(analytics) - min(analytics) < 21):
        type_profile = "Уплощенный"
        type_profile_info = type_profile_upl
    analytics_notes = [TB_F, TB_L, TB_K]
    analytics_clinic = [TB_1, TB_2, TB_3, TB_4, TB_5, TB_6, TB_7, TB_8, TB_9, TB_0]
    for i in analytics_clinic:
        if (i > 73):
            rating_profile += [
                "- Есть клинические шкалы выше 73 Тб. Возможно профиль не отражает действительную картину. Требуются иные исследования."]
            break
    for i in analytics_clinic:
        if (i > 70 and index_welsh == "Сомнительная достоверность"):
            rating_profile += [
                "- Индекс Уэлша определяет сомнительную достоверность и есть клинические шкалы выпадающие за 70 Тб."]
            break
    an = 0
    for i in analytics:
        if (analytics[2] > i):
            an += 1
    if (an == 12):
        rating_profile += ["- Шкала К самая высокая в профиле. Следует 'поднять' все клинические шкалы на 10 - 12 Тб."]
    an = 0
    for i in analytics:
        if (analytics[0] > 70 and i > 70):
            an += 1
        else:
            an = 0
    if (an > 0):
        rating_profile += [
            "Шклала F больше 70 и остальные шкалы до 70 Тб. Следует провести ретестирование по этой шкале (Возможно это характеризует начало кризиса)."]
    if (SB_L > 8):
        rating_profile += ["Сырое значение L больше 8 Сб."]
    if (type_profile == "Утопленный"):
        rating_profile += ["Тип профиля 'Утопленный'."]
    razdel_3 = True
    razdel_4 = True
    if len(rating_profile) == 1:
        rating_profile = ["Профиль не имеет признаков ограничений для исследования."]
    else:
        razdel_3 = False
        razdel_4 = False
        rating_profile = [
                             "Профиль не подлежит интерпретации. Можно только рассматривать сочетания шкал L, F, K. Причины: "] + rating_profile[
                                                                                                                                  1:]
    L_Discribe = str()
    F_Discribe = str()
    K_Discribe = str()
    if (SB_L > 1 and TB_L < 5):
        L_Discribe = "- (L 2-4 Сб) Гибкая конформность."
    elif (SB_L > 4):
        L_Discribe = "- (L от 5 Сб и более ) Относительный эмоциональный, психоэмоциональный комфорт."
    elif (SB_L < 5 and SB_L < SB_F):
        L_Discribe = "- (L Ниже 5 Сб и ниже F) Не использование инфантильных форм лжи в обыденной жизни."
    elif (SB_L > -1 and SB_L < 3 and TB_F > 69 and TB_K > 69):
        L_Discribe = "- (L 0 - 2  Сб и F и  К выше  70) Относительный эмоциональный, психоэмоциональный комфорт."
    elif (SB_L > -1 and SB_L < 5 and TB_4 > 69):
        L_Discribe = "- (L 0 Сб и 4 более 70 Тб) Нонконформизм."
    if (SB_F < SB_L and SB_F < SB_K):
        F_Discribe = "- (F Ниже L и K) Вероятное отрицание паталогий и расстройств (инфантильный защитный механизм)."
    elif (TB_F < 56):
        F_Discribe = "- ( F < 55 Тб) Отсутствие намеренного искажения результатов тестирования."
    elif (TB_F > 59):
        F_Discribe = "- ( F > 60 Тб) Возможна фрустрация."
    elif (TB_F > 69):
        F_Discribe = "- ( F > 70 Тб) Возможно крайнее своеобразие восприятия. Призыв о помощи."
    elif (TB_F > 89):
        F_Discribe = "- ( F > 90 Тб) Возможно искажение испытуемым результатов тестирования."
    elif (TB_F > 109):
        F_Discribe = "- (F>110 Тб) Возможно наличие рентной установки испытуемого (аггравация или симуляция). Рекомендовано патопсихологическое исследование."
    elif (TB_F > 99 and TB_F < 111):
        F_Discribe = "- ( 100 < F <110 Тб) Возможно психотическое (предпсихотическое) состояние испытуемого."
    elif (TB_F > 69 and TB_F < 91 and TB_K < 56 and TB_2 > 69 and TB_7 > 69):
        F_Discribe = "- Важно: (F 70-90 Тб, К ниже 55 Тб,  2 и 7 пики) демонстрмруют возможную субпсихотическую тревогу. Рекомендована консультация психиатра."
    elif (TB_F > 64 and TB_F < 76 and TB_4 > 69 and TB_6 > 69 and TB_8 > 68 and TB_9 > 69):
        F_Discribe = "- (F 65-75, пики 4,6,8,9) Возможно отношение испытуемого к субкультуре или возможно испытуемый имел мотив произвести шокирующее впечатление на экпериментатора."
    elif (TB_F > 64 and TB_F < 76 and TB_8 > 69):
        F_Discribe = "- (F 65-75, пик 8) Возможно 'подлинное своеобразие испыуемого'."
    elif (TB_F > 64 and TB_F < 76):
        F_Discribe = "- (F 65-75) Возможно для данного испытуемого характерны подростковые реакции."
    if (SB_K > 7 and SB_K < 17):
        K_Discribe = "- (K 8-16 Сб) Норма. Возможно испытуемый был откровенен."
    elif (TB_K > 64):
        K_Discribe = "- (K 65 Тб и выше) Возможна высокая социальная активность."
    elif (TB_K < 56):
        K_Discribe = "- (K ниже 55 Тб) Возможны сложности в формировании контакта с терапевтом."
    elif (TB_K > 69):
        K_Discribe = "- (K выше 70 Тб) Закрытость в передаче личной информации. Резистентность к терапии."
    elif (TB_K < TB_F):
        K_Discribe = "- (K меньше F) Возможно склонность к преувелчинию тяжести состояния и расстройств как тенденция, так же косвенный показатель рефлексии."
    elif (TB_K > 47 and TB_K < 53):
        K_Discribe = "- (К от 48 до 52 Тб) Интериоризированные социальные нормы."
    elif (TB_K > max(TB_F, TB_L, TB_1, TB_2, TB_3, TB_4, TB_5, TB_6, TB_7, TB_8, TB_9, TB_0)):
        K_Discribe = "- (К выше всех шкал) Очень высокая степень закрытости, не желание принимать участие в тестировании. Целесообразно весь профиль поднять на 10 баллов."
    elif (TB_K > 59):
        K_Discribe = "- (К выше 60 Тб) Возможна высокая социальная активность."
    elif (TB_K < 51):
        K_Discribe = "- (К ниже 50 Тб) пассивная личностная позиция. Внешний локус контроля. Резистентность к терапии."
    elif (TB_K > 64):
        K_Discribe = "- (К выше 65 Тб) Возможна закрытая личностная позиция."
    description_line = []
    description_scale = []
    if (razdel_4 and razdel_3):
        if TB_1 > 69 or (TB_1 > 49 and TB_1 > TB_2):
            description_line += ["""1 Тревоги (Ипохондрии, Соматизации тревоги).
                                    \nОписание - Соматизация тревоги, измеряет степень выраженности ипохондрических черт личности, когда не решенные психологические проблемы вытесняются в соматическую сферу
                                    \nАкцентуация - Синзетивно-тревожная или конформная
                                    \nВыше 70 Тб - Возможны:повышенная чувствительность, реагирование на стресс путем ухода в болезнь, вегетативеая возбудимость, постоянная озабоченность своим физическим состоянием, пессимизм, неверие у успех, несговорчивость, упрямство.
                                    \nЗащитный механизм - Соматизация тревоги.
                                    \nВид терапии - Высокая резистентность – подходит телесно-ориентированная, танцевальная, арт-, музыко-, цвето-психотерапия (любая, которая связана с телом, ощущением, движением)."""]
        if TB_2 > 69 or (TB_2 > 49 and TB_2 > TB_1 and TB_2 > TB_3):
            description_line += ["""2 Тревоги и депресии
                                    \n- Характеризует состояние (подавленность, снижение фона настроения, высокая степень истощаемости). Следует уделять особое внимание внимание в случае превышения середины профиля, превышения над 1 и 3.
                                    \nАкцентуация - Дистимная или тревожно мнительная.
                                    \nВыше 70 Тб - Возможны: внутрення напряженность, неуверенность, тревога, снижение настроения, пониженная самооценка, пессимистическая оценка перспективы, аутоагрессия. 
                                    \nЗащитный механизм - Компенсация (отказ от реализации своих намерений).
                                    \nВид терапии - Тактикой терапии возможно будет поиск обесценных потребностей и желаний."""]
        if TB_3 > 69 or (TB_3 > 49 and TB_3 > TB_2 and TB_3 > TB_4):
            description_line += ["""3 Шкала Вытеснения
                                    \nОписание - Измеряет степень выраженности истероидных,  демонстративных черт личности.
                                    \nАкцентуация - Демонстративная (Истероидная).
                                    \nВыше 70 Тб - Возможно демонстративное поведение. Возможны: недостаточность развитости внутреннего мира, бесплановость и хаотичность, высокая самооценка, недостаточная критичность в оценке ситуации и поведения, изюегание ответсвенности в состоянии стресса, ориентировка на внешнее окружение. Высокая резистентность к терапии.
                                    \nЗащитный механизм - Регресс и вытеснение. Устранение тревоги за счет вытеснения из сознания обуславливающих ее факторов и формирование конверсионного симптома
                                    \nВид терапии - В начале терапии обычно успешно, но в дальнейшем возможно возникновение чувства пртеста к настойчивому вмещательству терапевта. На симптоматическую терапию реагируют хорошо, но симптоматика быстро возвращается или трансформируется. Лучше арт-терапия или другое прямое воздействие на эмоции через терапию искусством (психодрама, музыкотерапия, рисование, лепка), гипноз."""]
        if TB_4 > 69 or (TB_4 > 49 and TB_4 > TB_3 and TB_4 > TB_6):
            description_line += ["""4 шкала Социальной психопатии.
                                    \nОписание - Реализация эмоциональной напряженности в непосредственном поведении.
                                    \nАкцентуация - Гипертимная или возбудимая
                                    \nВыше 70 Тб - Возможно: психопатия (шизоидная или истероидная). Нонкомформизм. Возможны: неприятие (осознание) социальных норм и обычаев, межличностная поверхность, эмоциональная холодность, социальная безответственность, стремление к немедленному удовлетворению своих потребностей, раздражительность, гневливость, бесстрашность.
                                    \nЗащитный механизм - Вытесненение и рационализация, немедленная реализация аффективных комплексов в актуальном поведении.
                                    \nВид терапии - Терапевтический прогноз плохой. Поведенческая психотерапия, гуманистическая и тактика социализации."""]
        if TB_6 > 69 or (TB_6 > 49 and TB_6 > TB_4 and TB_6 > TB_7):
            description_line += ["""6 шкала Ригидности аффекта
                                    \nОписание - Измеряет степень выраженности застревающих или паранойяльных черт личности
                                    \nАкцентуация - Эпилептоидная
                                    \nВыше 70 Тб - Возможны: сверхнормативность, ригидность, самоуверенность, нонкомформизм, экстрапунитивные реакции, подозрительность, упорство, усидчивость, консерватизм.
                                    \nЗащитный механизм - Проекция и рационализация
                                    \nВид терапии - Высокая за счет некоррегируемости установок. Рациональная психотерапия, неоповеденческие методы."""]
        if TB_7 > 69 or (TB_7 > 49 and TB_7 > TB_6 and TB_7 > TB_8):
            description_line += ["""7 шкала Фиксации тревоги
                                    \nОписание - Измеряет степень выраженности исходно-тревожных черт личности.
                                    \nАкцентуация - Психастеническая, тревожно-мнительная (сенситивная).
                                    \nВыше 70 Тб - Возможно: низкая способность к вытеснению тревоги и повышенное внимание к отрицательным сигналам."" Возможны: неуверенность в своих возможностях, стремление к безопасности и защите, поведение по принципу "избегание неудач", склонность к ритуализации, сдержанность в проявлении своих чувств.
                                    \nЗащитный механизм - Избегание неудач. Рационализация и интеллектуализация с формированием ограничительного поведения.
                                    \nВид терапии - 1. Если пик 7 и пик 2 Гипостения (тревожно-фобический синдром) , любые виды терапии 2. пик 7 и снижение 2 Гиперстения) высокая резистентность терапии (КПТ)."""]
        if TB_8 > 69 or (TB_8 > 49 and TB_8 > TB_7 and TB_8 > TB_9):
            description_line += ["""8 шкала Аутизации
                                    \nОписание - Измеряет степень выраженности шизоидных черт личности
                                    \nАкцентуация - Шизоидная
                                    \nВыше 70 Тб - Возможно: эмоциональное уплощение, эмоциональная тупость, эмоциональная холодность, своеобразие восприятия, плохое понимание мотивов и эмоции других людей, странности поведения, выборов. Нонкомформизм.
                                    \nЗащитный механизм - Аутизация или дистанцирование. """]
        if TB_9 > 69 or (TB_9 > 49 and TB_9 > TB_8 and TB_9 > TB_0):
            description_line += ["""9 шкала Гипомании
                                    \nОписание - Измеряет степень выраженности гипоманиакального расстройства, гипоманиакальных черт
                                    \nАкцентуация - Гипертимная или экзальтированная
                                    \nВыше 70 Тб - Возможно: отсутствие чувства меры, нарушение чужих личных границ,, поверхностность и неустойчивость интересов, отрицание межличностных конфликтов, ощущение радости, удовольствия.
                                    \nЗащитный механизм - Отрицание затруднений в межличностных контактах."""]
        if TB_0 > 69 or (TB_0 > 49 and TB_0 > TB_9):
            description_line += []
        if TB_1 <= 49:
            description_line += ["""1 Тревоги (Ипохондрии, Соматизации тревоги).
                                    \nОписание - Соматизация тревоги, измеряет степень выраженности ипохондрических черт личности, когда не решенные психологические проблемы вытесняются в соматическую сферу
                                    \nЗападение - Предположительно характерны деятельность и энергичность (разрешение трудностей адаптивными формами поведения, бодрость."""]
        if TB_2 <= 49:
            description_line += ["""2 Тревоги и депресии
                                    \n- Характеризует состояние (подавленность, снижение фона настроения, высокая степень истощаемости). Следует уделять особое внимание внимание в случае превышения середины профиля, превышения над 1 и 3.
                                    \nЗападение - Возможны: ощущение бодрости и активности(не всегда выражено в поведении), ощущении своей значимости, бодрости."""]
        if TB_3 <= 49:
            description_line += ["""3 Шкала Вытеснения
                                    \nАкцентуация - Демонстративная (Истероидная).
                                    \nЗащитный механизм - Регресс и вытеснение. Устранение тревоги за счет вытеснения из сознания обуславливающих ее факторов и формирование конверсионного симптома"""]
        if TB_4 <= 49:
            description_line += ["""4 шкала Социальной психопатии.
                                    \nОписание - Реализация эмоциональной напряженности в непосредственном поведении.
                                    \nЗападение - Возможно: предположительно конформный тип личности. Возможны послушность, стремление соблюдать общепринятые нормы, сдержанность."""]
        if TB_6 <= 49:
            description_line += ["""6 шкала Ригидности аффекта
                                    \nОписание - Измеряет степень выраженности застревающих или паранойяльных черт личности
                                    \nЗападение - Возможны: гибкость мышления, неустойчивость переживаний, доверчивость."""]
        if TB_7 <= 49:
            description_line += ["""7 шкала Фиксации тревоги
                                    \nОписание - Измеряет степень выраженности исходно-тревожных черт личности.
                                    \nЗападение - Возможно: отсутствие фиксации тревоги (косвенно, бесчувствие), решительность, уверенность в себе."""]
        if TB_8 <= 49:
            description_line += ["""8 шкала Аутизации
                                    \nОписание - Измеряет степень выраженности шизоидных черт личности
                                    \nЗападение - Возможно: стандартность поведения, банальность мышления, общительность."""]
        scale_comb_2 = True
        scale_comb_1 = True
        scale_comb_9 = True
        scale_comb_8 = True
        if (TB_2 > 70 and TB_7 > 70):
            scale_comb_2 = False
        if (TB_3 > 70 and TB_1 > 70):
            scale_comb_1 = False
        if (TB_4 > 70 and TB_9 > 70):
            scale_comb_9 = False
        if (TB_6 > 70 and TB_8 > 70):
            scale_comb_8 = False
        middle_profile = sum(analytics_clinic) / 10
        if (TB_2 > 70 and TB_9 < TB_0):
            description_scale += ["""(!) Вероятность суицидальных намерений
            """]
        if (max(analytics_clinic) < 70 and TB_2 > TB_1 and TB_9 < TB_8):
            description_scale += ["""Вероятность суицидальных мыслей (смотреть разброс).
    """]
        if (TB_F > 70 and TB_4 > 70 and TB_6 > 70 and TB_8 > 70):
            description_scale += ["""Возможно богемный образ жизни. Если нет то - консультация психотерапевта.
    """]
        if (TB_K >= 48 and TB_K <= 52):
            description_scale += ["""Интериоризация.
    """]
        if (TB_K > TB_F and TB_K > TB_L and TB_K > max(analytics_clinic)):
            description_scale += ["""При анализе профиля следует учесть, что весь профиль следует поднять на 10-12 Тб. Программа этого не делает автоматически.
    """]
        if (TB_F > TB_K and TB_F > TB_L and TB_F > max(analytics_clinic)):
            description_scale += ["""Сдедует провести ретестирование. Если результат повотриться, то существует вероятность стадии или начала эндогенного процесса, или кризиса.
    """]
        if (TB_K > TB_L and TB_8 > TB_7 and TB_0 > TB_9):
            description_scale += ["""Возможна закрытость как личностное образование.
    """]
        if (TB_2 < TB_1 and TB_2 < TB_3):
            description_scale += ["""Возможна конверсионная истерия (проявляется в демонстрации соматических расстройств для объяснения жизненных затруднений).
    """]
        if (TB_2 < middle_profile and TB_2 < TB_1 and TB_2 < TB_3):
            description_scale += ["""Возможно ощущение бодрости, активности, но не всегда выражено в поведении.
            """]
        if (TB_2 > 55 and TB_2 > TB_1 and TB_2 > TB_3):
            description_scale += ["""Возможна депрессия.
    """]
        if (TB_3 > TB_2):
            description_scale += ["""Возможен демонстративный радикал
    """]
        if (TB_3 < TB_2):
            description_scale += ["""Возможно плохо работающий механизм вытеснения отрицательных сигналов (угрюмость, замкнутость).
    """]
        if (TB_4 > TB_3 and TB_4 < TB_5 and TB_9 > TB_8 and TB_9 < TB_0 and TB_4 >= 55 and TB_4 < 70 and TB_9 >= 55 and TB_9 < 70):
            description_scale += ["""Возможна вербальная агрессия
    """]
        if (TB_4 < middle_profile and TB_4 < TB_3 and TB_K > TB_L):
            description_scale += ["""Вероятно конформный тип личности.
    """]
        if (TB_4 < min(analytics_clinic)):
            description_scale += ["""Возможна аутоагрессия, размытость границ.
    """]
        if (TB_4 > middle_profile and TB_7 > middle_profile and TB_9 > middle_profile):
            description_scale += ["""Возможны раздражительность, нетерпимость, сензитивность.
    """]
        if (TB_6 > TB_5 and TB_6 < 70):
            description_scale += ["""Возможны хорошее целеполагание, способность держать удар, самоуверенность, скуповатость, трудолюбие, тяга к карьере, надежность.
    """]
        if (TB_6 < middle_profile and TB_6 < TB_5):
            description_scale += ["""Возможна гибкость мышления.
    """]
        if (TB_6 < TB_5 and TB_K > TB_L):
            description_scale += ["""Возможно тестируемый, узнавая в тексте свои  черты (6), категорически это отрицал.
    """]
        if (TB_7 > 70):
            description_scale += ["""Вероятно выраженные тревожные черты ("Ловец отрицательных сигналов").
    """]
        if (TB_7 > 75 and TB_7 < 80):
            description_scale += ["""Возможно психастения.
    """]
        if (TB_7 < middle_profile and TB_7 < TB_6):
            description_scale += ["""Возможно отсутствие фиксации тревоги (косвенно - бесчуствие).
    """]
        if (TB_7 > 60 and TB_8 > 60):
            description_scale += ["""Возможен бред совершества.
    """]
        if (TB_8 < middle_profile and TB_8 < TB_7):
            description_scale += ["""Возможно банальность мышления.
    """]
        if (TB_9 < middle_profile and TB_9 < 0):
            description_scale += ["""Возможно депрессия
    """]
        if (TB_9 > TB_0):
            description_scale += ["""Возможно социальная экстраверсия.
    """]
        if (TB_9 < TB_0):
            description_scale += ["""Возможно социальная интроверсия.
    """]
        if (TB_9 > TB_0 and TB_9 > 25):
            description_scale += ["""Возможно легкость вступления в контакты, широта общения.
    """]
        if (TB_9 < TB_0 and TB_9 > 25):
            description_scale += ["""Возможна социальная изоляция.
    """]
        if (abs(TB_9 - TB_0) > 0 and abs(TB_9 - TB_0) < 3):
            description_scale += ["""Возможно социальная интроверсия (м.б. депрессия).
    """]
        if (TB_2 > middle_profile and TB_9 > middle_profile and TB_2 > TB_1 and TB_9 > TB_8):
            description_scale += ["""Возможна эмоциональная лабильность.
    """]
        if (TB_1 > TB_2 and TB_2 > middle_profile):
            description_scale += ["""Возможно снижение настроения, затруднение в социальных контактах, тревога за состояние своего здоровья.
    """]
        if (TB_2 > middle_profile and TB_4 > middle_profile and TB_6 > middle_profile and TB_9 > middle_profile):
            description_scale += ["""Возможно реактивное состояние после совершенного асоциального поступка.
    """]
        if (TB_3 > middle_profile and TB_4 > middle_profile):
            description_scale += ["""Возможно эмоциональная незрелость, контроль ассоциальных импульсов, склонность к конформизму.
    """]
        if (TB_3 > TB_2 and TB_3 > TB_4 and TB_K > middle_profile):
            description_scale += ["""Повышение К делает более тонкими прявления демонстративности.
    """]
        if (TB_3 > middle_profile and TB_7 > middle_profile and TB_9 > middle_profile):
            description_scale += ["""Возможна эмоциональная лабильность.
    """]
        if (TB_4 > middle_profile and TB_6 > middle_profile):
            description_scale += ["""Возможна дисфория.
    """]
        if (TB_4 > TB_3 and TB_4 > TB_5 and TB_7 > TB_6 and TB_7 > TB_8):
            description_scale += ["""Возможно глубинная личностная дисгармония.
    """]
        if (TB_6 > middle_profile and TB_7 > middle_profile):
            description_scale += ["""Возможно проявление тревожно-застпевающих черт.
    """]
        if (TB_6 > middle_profile and TB_8 > middle_profile):
            description_scale += ["""Возможно проявление шизоидно-параноидальных черт.
    """]
        if (TB_7 > middle_profile and TB_8 > middle_profile):
            description_scale += ["""Возможно проявление синзитивно-шизоидных черт.
    """]
        if (TB_8 > middle_profile and TB_9 > middle_profile):
            description_scale += ["""Возможно проявление экспансивно-шизоидных черт.
    """]
        if (TB_4 > TB_3 and TB_4 > TB_5 and TB_4 > 55 and TB_6 > TB_5 and TB_6 > TB_7 and TB_6 > 55 and TB_9 > TB_8 and TB_9 > TB_0 and TB_9 > 55):
            description_scale += ["""Возможно агрессивное поведение, сопровождающееся неконтролируемым гневом.
    """]
        if (TB_1 > 70 and TB_4 > 70):
            description_scale += [""" Беспокойство о состоянии своего физического здоровья блокирует ассоциальные проявления. Соматические жалобы используются для давления на окружающих с целью получения преимуществ.
    """]
        if (TB_1 > 70 and TB_2 > 70):
            description_scale += ["""Возможны: снижение настроения, затруднения в социальных контактах,  раздражительность, тревога за состоянием своего здоровья, в соматических жалобах выражается ощущение угрозы и недостаточность внимания со стороны окружающих.
    """]
        if (TB_1 > 70 and TB_6 > 70):
            description_scale += [""" Возможны: трудности в межличностных связях; наличие хорошо разработанной концепции заболевания.
    """]
        if (TB_1 > 70 and TB_7 > 70):
            description_scale += ["""  Чрезмерная озабоченность своим соматическим благополучием, имеется страх перед конкретным заболеванием.
    """]
        if (TB_1 > 70 and TB_8 > 70):
            description_scale += [""" Забота о физическом здоровье может использоваться как средство, позволяющее рационально  объяснять отчужденность от окружающих.
    """]
        if (TB_1 > 70 and TB_9 > 70):
            description_scale += [""" Повышенная активность, высокое честолюбие и самооценка сочетаются с невозможностью добиться желаемого положения и реализовать актуальные устремления, и возникает тревога, которая относится за счет соматического состояния. Напряженность и активное стремление к соматической терапии, демонстративный оптимизм и стремление подчеркнуть свою стойкость перед лицом тяжелого недуга.
    """]
        if (TB_2 > 70 and TB_3 > 70):
            description_scale += [""" Демонстрация слабости, беспомощности и вины, направленная на получение сочувствия и поддержки со стороны окружающих, используется как средство давления на близких людей.
    """]
        if (TB_2 > 70 and TB_4 > 70):
            description_scale += [""" Возможно затруднение социальной адаптации и отражает тенденцию к тревоге, связанную с неспособностью строить свое поведение в соответствии с принятыми нормами. Склонность к самоупреку и смообвинению  при нарушении социальных норм.
    """]
        if (TB_2 > 70 and TB_6 > 70):
            description_scale += ["""Дисгармоничность, выраженная одновременным существованием потребности в доверительных отношениях и стремлении переносить вину на других. Возможны трудности в межличностных связях и нарушение социальной адаптации.
    """]
        if (TB_2 > 70 and TB_7 > 70):
            description_scale += [""" Возможен тревожно-фобический симптом. Картографирование внутреннего мира, принципиальность в некоторых вопросах, стереотипность мышления и поведения. Трудность принятия решений. Пониженная самооценка, пессеместическая оценка перспектив сочетается с постоянной внутренней напряженностью.
    """]
        if (TB_2 > 70 and TB_8 > 70):
            description_scale += [""" Чувство недостаточной связи с окружением, неудовлетворенной потребности в контактах выражается в нарастании тревоги и подавленности. Амбивалентное отношение к окружающим порождает нараяду со стремлением к контактам угрюмую недоверчивость.
    """]
        if (TB_2 > 70 and TB_9 > 70):
            description_scale += [""" Возможно чередование коротких аффективных фаз разной направленности, когда в период фаз одной направленности сохраняется четкое воспоминание о фазах другого знака. Не исключено сочетание ощущения собственной неповторимости, значимости, высоких возможностей с беспокойством по поводу непризнания этих качеств окружающими.
    """]
        if (TB_2 > 70 and TB_1 > 70):
            description_scale += [""" В социальных контактах снижению настроения сопутствует раздражительность и тревога за состояние своего здоровья. Неудовлетворенная симбиотическая тенденция. В соматических жалобах выражается ощущение угрозы и недостаточность внимания со стороны окружаюжих. 
    """]
        if (TB_3 > 70 and TB_4 > 70):
            description_scale += [""" Стремление ориентироваться на внешнюю оценку препятствует прямому ассоциальному поведению, позволяет контролировать асоциальные импульсы в отношении малознакомых людей. Враждебность и нежелание считаться с интересами окружающих проявляются главным образом в отношении с близкими людьми.
    """]
        if (TB_3 > 70 and TB_6 > 70):
            description_scale += ["""Возможны трудности в межличностных связях. Возможно проявление агрессии к членам ближнего окружения (Дисгармоничность обусловлена сочетанием стремлением ориентироваться на внешнюю оценку и ощущением враждебности со стороны окружающих, а также сочетанием ориентации на ситуационнно обусловленное поведение со склонногстью к следованию ригидным концепциям. Подавление подозрительности и агрессивности, декларация своего положительного отношения к окружающим).
    """]
        if (TB_3 > 70 and TB_7 > 70):
            description_scale += [""" Тревожно-фобические рассторойства сочетаются с тенеденцией демонстрации своего состояния, стремлением вызвать покровительственное  отношение окружающих, подчеркнутой беспомощностью. Пункутальность, тщательнсоть, основательность и снижение социальной спонтанности дисгармонируют с демонстративностью, эгоцентричностью, стремлением быть в центре внимания. При высокой потребности во внимании, признании и демонстративном поведении сохраняется значительная критичность и болезненное реагирование на замечания и отрицательные сигналы.
    """]
        if (TB_3 > 70 and TB_8 > 70):
            description_scale += [""" Дисгармоничность - парадоксальное сочетание ориентации на актуальное поведение, на внешнюю оценку, на одобрение окружающих со склонностью строить свое поведение, исходя из внутренних критериев, и трудностями в межличностных коммуникациях. Формирование круга своих знакомств и контактов, в котором значимость безоговорочно признается.
    """]
        if (TB_3 > 70 and TB_9 > 70):
            description_scale +=[""" Повышенная самооценка, способность игнорировать затруднения, большая, но плохо организованная активность сочетается с высокой способностью к вытесненнию отрицательных сигналов, демонстративностью, эмоциональной незрелостью и эгоизмом. 
    """]
        if (TB_4 > 70 and TB_6 > 70):
            description_scale += [""" Склонность к ассоциальному поведению возрастает за счет сочетания пренебрежением социальными нормами со стойкой реализации этой тенденции. В связи с этим вохрастает трудность социальной адаптации. Стойкая недоброжелательность к окружающим, угрюмость, вспышки агрессии, трудность и неприятность в общении.
    """]
        if (TB_4 > 70 and TB_7 > 70):
            description_scale += [""" Тщательный контроль делает невозможным открытое проявление асоциальных тенденций. Возможно снижение ассоциальных тенденций поведения и проявление экстрапунитивных тенденций. Удовлетворение экстрапунтивных тенденций осуществляется за счет актуализации чувсва тревоги и вины у окружающих.
    """]
        if (TB_4 > 70 and TB_8 > 70):
            description_scale += [""" В результате нарушения межличностных связей нарушается социальная адаптация. Асоциальные поступки совершаются в результате недоразумений, неприспособленности к тем или иным условиям, неспособности четко осознать социальную норму и своеобрахного подхода к ситуации. Неспососбность правильно организовывать и контролировать свои контакты и своеобразие мышления могут обуславливать связь с девиантными группами. Отношение к окружающим с недоверием, восприяите их как источника потенциальной опасности или как людей чуждых. Постоянное ощущение угрозы может толкать на превентивное нападение.
    """]
        if (TB_4 > 70 and TB_9 > 70):
            description_scale += [""" Постоянное влечение к переживаниям, к внешенй возбуждающей ситуации. Если это влечение не удовлетворяется, легко возникает чувство скуки, разряжемое в опасных, иногда разрушительных действиях, представляющихся постороннему наблюдателю бессмысленными и лишенные основания. Пренебрежение существующими правилами и обычаями, протест против моральных и этических норм реализуется активно, зачастую без всякой коррекции своего поведения, которое представляет угрозу для самого человека. Возможность совершения правонарушений.
    """]
        if (TB_4 > 70 and TB_5 > 70 and TB_9 > 55):
            description_scale += [""" Возможно проявление выспышек агрессии
    """]
        if (TB_6 > 70 and TB_7 > 70):
            description_scale += ["""Дисгармоничное сочетание склонности к образованию ригидных концепций с высоким уровнем тревожности.
    """]
        if (TB_6 > 70 and TB_8 > 70):
            description_scale += ["""Склонность к формированию трудно корректируемых концепций, связанных с представлением о наличии угрожающих или опасных действий окружающих (подозрительность). Выраженная избирательность восприятия, при которой отбирается преимущественно информация, подкрепляющая уже сформированную концепцию. Утрата контакта с реальностью, замена реального общества псевдообществом, представляющим собой совокупность собственных проекций. В клинике проявляется бредовыми синдромами.
    """]
        if (TB_6 > 70 and TB_9 > 70):
            description_scale += [""" Возможна последовательность и целенаправленность поведения, организованного вокруг определенной концепции. Однако ощущение враждебности со стороны окружения может осложнять межличностные контакты. Стремление утверждать свое превосходство и использовать окружающих для достижения своих целей.
    """]
        if (TB_7 > 70 and TB_8 > 70):
            description_scale += ["""С клонность ориентироваться на внутренние критерии и коммуникативные затруднения сочетаются с вызванной этими затруднениями тревожностью. Депрессивные тенденции, отмечающиеся вне зависимости от уровня профиля на шкале 2, сочетаются с раздражительностью и тревожностью или ощущением повышенной утомляемости и апатии.
    """]
        if (TB_7 > 70 and TB_9 > 70):
            description_scale += [""" Высокая активность обуславливает легкость совершения тех или иных поступков, часто недостаточно продуманных, а высокая тревожность приводит к последующему тщательному анализу своих действий, постоянным сомнением в правильности уже совершенного. Легко возникает чувство вины и сожаления в связи с уже минувшей ситуацией, но это не изменяет поведения в будущем.
    """]
        if (TB_7 > 70 and TB_2 < 60):
            description_scale += [""" Возможно гиперстения. Ограничительное поведение,принципиальность, чувство вины, низкая рефлексия (выхолощена тревога).
    """]
        if (TB_8 > 70 and TB_9 > 70):
            description_scale += ["""Аутизация, ориентировка на внутренние критерии, затруднения межличностных контактов сочетаются с повышенной отвлекаемостью и неспособностью длительно фиксировать внимание. Такое сочетание свидететльствует о недостаточной способности к последлвательным действиям и логическим построениям.
    """]
        if ((TB_1 == max(analytics_clinic) and TB_1 > max(analytics_notes)) or TB_1 > TB_2 or TB_1 > 60):
            description_scale += [""" Возможны: озабоченность своим физическим состоянием, пессимизм, неверие у успех, несговорчивость, упрямство.
    """]
        if ((TB_2 == max(analytics_clinic) and TB_2 > max(analytics_notes)) or (TB_2 > TB_1 and TB_2 > TB_3) or TB_2 > 60):
            description_scale += [""" Возможны:  озабоченность своим физическим состоянием, пессимизм, неверие в успех, несговорчивость упрямство.
    """]
        if ((TB_3 == max(analytics_clinic) and TB_3 > max(analytics_notes))or (TB_3 > TB_2 and TB_3 > TB_4) or TB_3 > 60):
            description_scale += ["""Возможны: высокий социальный интеллект, ориентированность на нормы, демонстративное поведение, эмоциональная лабильность и инфантильность, эмоциональная мимикрия,межличностная поверхностность, фантазирование, манипулятивность.
    """]
        if ((TB_4 == max(analytics_clinic) and TB_4 > max(analytics_notes)) or (TB_4 > TB_2 and TB_4 > TB_6) or TB_4 > 60):
            description_scale += [""" Нонкомформизм. Возможны: неприятие (осознание) социальных норм и обычаев, межличностная поверхность, эмоциональная холодность, социальная безответственность.
    """]
        if ((TB_6 == max(analytics_clinic) and TB_6 > max(analytics_notes)) or (TB_6 > TB_4 and TB_6 > TB_7) or TB_6 > 65):
            description_scale += [""" Возможны: сверхнормативность, ригидность, самоуверенность, нонкомформизм, экстрапунитивные реакции, подозрительность, упорство, усидчивость, консерватизм.
    """]
        if ((TB_7 == max(analytics_clinic) and TB_7 > max(analytics_notes)) or (TB_7 > TB_6 and TB_7 > TB_8) or TB_7 > 55):
            description_scale += [""" Возможно: высокая тревога – тревога всегда требует ограничения, внутреннее картографирование пространства жизни, схематизация внутреннего мира – принципиальность, постоянная ревизия собственного поведения – стереотипность поведения и мышления – трудность принятия решения, моральность.
    """]
        if (TB_1 > 50 and TB_2 < TB_1 and TB_3 > 50):
            description_scale += [""" Конверсионная истерия (демонстрация соматических расстройств для объяснения жизненных затруднений). Степень выраженности зависит от величины 1 и 2.
    """]
        if (TB_7 > TB_6 and TB_9 > TB_8):
            description_scale += [""" Возможна эмоциональная лабильность.
    """]
        if (TB_3 > TB_2 and TB_3 > TB_4 and TB_K > 60 and TB_F < 50):
            description_scale += [""" 3 нивелируется (тонкое проявление демонстративных черт, редкое проявление конверсионного симптома).
    """]
        if (TB_4 > TB_3 and TB_9 > TB_8):
            description_scale += [""" Возможна вербальная агрессия.
    """]
        if (TB_4 == min(analytics_clinic)):
            description_scale += [""" Аутоагресссия. Косвенный признак тревожного типа личности (даже если не поднята 7). Черты: размытость Я, боязливость, нерешительность. Возможны : зависимости, сверхценные идеи привязанности, нет собственного мнения.
    """]
        if (TB_4 < 50 and TB_K > 50):
            description_scale += [""" Предположительно конформный тип личности.
    """]
        if (TB_4 > 50):
            description_scale += [""" Возможны: сверхценность, агрессия, импульсивность.
    """]
        if (TB_4 > 70 and TB_1 > 55):
            description_scale += [""" Возможно чем выше 1, тем меньше ассоциальных проявлений (соматические жалобы как инструмент давления на окружающих).
    """]
        if (TB_4 > 55 and TB_7 > 55 and TB_9 > 55):
            description_scale += [""" Возможны: раздражительность, синзетивность.
    """]
        if (TB_4 < 50 and TB_7 > 55):
            description_scale += [""" Возможны: бред безупречности, педантизм.
    """]
        if (TB_4 < 50 and TB_7 > 55 and TB_5 < 50 and type_profile == "Утопленный"):
            description_scale += [""" Возможно алкоголизм.
    """]
        if (TB_3 > 55 and TB_4 > 55):
            description_scale += [""" Возможна эмоциональная незрелость (Ориентировка на внешнюю оценку препятствует прямому ассоциальному поведению). Возможна "канализированная и обоснованная" враждебность к отдельным членам ближнего окружения.
    """]
        if (TB_6 > 50 and TB_6 < 70):
            description_scale += [""" Возможны: хорошее целеполагание, хорошая способность держать удар, самоуверенность, прижимистость, скупость, "обстоятельный тормоз", трудолюбие, тяга к карьере, амбициозность, размеренность, последовательность, создает "ощущение комфорта" и надежности.
    """]
        if (TB_6 < 50 and TB_K > 55):
            description_scale += [""" Возможно 6 была занижена испытемым (следует повысить 6 относительно середины профиля на величину его фактического отклонения от середины профиля).
    """]
        if (TB_7 > 55 and TB_8 > 55):
            description_scale += [""" Возможен бред совершества.
    """]
        if (TB_6 > 55 and TB_7 > 55 and TB_8 > 55):
            description_scale += [""" Возможны элементы дезадаптации (аутизация, избегание неудач, повышение чувствительности, эмоциональная тупость к окружающим, бред отношений-проекция).
    """]
        if (TB_2 > 60 and TB_7 > 60 and TB_9 < 50):
            description_scale += [""" Возможны: мрачная окраска сиуации, перспектив; снижение продуктивности, инициативы, ощущение подавленности.
    """]
        if (TB_9 > 50 and TB_9 < 70):
            description_scale += [""" Повышенный фон настроения, не испытывает трудности в межперсональных отношениях, не свойственны чувство вины и обиды, отрицание трудностей жизни, переориентации цели, характерен метод проб и ошибок.
    """]
        if (TB_9 < TB_0 and TB_9 < 50):
            description_scale += [""" Возможно депрессивное сосотояние.
    """]
        if (abs(TB_9 - TB_0) > -3 and abs(TB_9 - TB_0) < 3):
            description_scale += [""" Возможна социальная интроверсия и депрессия.
    """]

    return render_template("report.html", title="Отчет о прохождении теста MMPI.",
                           name=information_user[1],
                           date=date_test, gender=gender, age=age, SB_L=SB_L,
                           SB_F=SB_F, SB_K=SB_K, SB_1=SB_1, SB_2=SB_2,
                           SB_3=SB_3, SB_4=SB_4, SB_5=SB_5, SB_6=SB_6,
                           SB_7=SB_7, SB_8=SB_8, SB_9=SB_9, SB_0=SB_0,
                           TB_L=TB_L, TB_F=TB_F, TB_K=TB_K, TB_1=TB_1,
                           TB_2=TB_2, TB_3=TB_3, TB_4=TB_4, TB_5=TB_5,
                           TB_6=TB_6, TB_7=TB_7, TB_8=TB_8, TB_9=TB_9,
                           TB_0=TB_0, index_welsh=index_welsh, rating_veracity=rating_veracity, androgyny=androgyny,
                           profile_tilt=profile_tilt, type_profile=type_profile, type_profile_info=type_profile_info,
                           rating_profile=rating_profile,
                           K_Discribe=K_Discribe, L_Discribe=L_Discribe, F_Discribe=F_Discribe,
                           description_line=description_line, description_scale=description_scale, code_welsh=code_welsh,
                           img_root=img_root, img_root_time=img_root_time, min_time_test=min_time_test, max_time_test=max_time_test,
                           time_test=time_test, middle_time_test=middle_time_test, attemps=attemps, quiz_attemps=quiz_attemps)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")


if __name__ == '__main__':
    conn = sqlite3.connect("kovesh.db")
    cur = conn.cursor()
    cur.execute("create table if not exists users ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT,"
                "age INT, "
                "email TEXT,"
                "date TEXT,"
                "gender TEXT,"
                "deleted TEXT)")
    conn.commit()
    quer = ', '.join(["quiz_" + str(i) + " TEXT, time_" + str(i) + " TEXT" for i in range(1, 378)])
    # print(quer)
    sql_q = f"create table if not exists test (id INTEGER PRIMARY KEY AUTOINCREMENT, id_user TEXT, date TEXT, {quer})"
    cur.execute(sql_q)
    conn.commit()
    sql_q = f"create table if not exists attemps (id INTEGER, quiz, attemp)"
    cur.execute(sql_q)
    conn.commit()
    conn.close()
    app.run(host='0.0.0.0', port='', debug=True)
