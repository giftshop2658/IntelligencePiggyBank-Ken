from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views, authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.urls import reverse

from .form import LoginForm, CreateUserForm, PictureForm, CalculationForm
from django.db import connection


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponse('登入成功')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('portfolio:home'))
            # return redirect(reverse('user_test:login_required_view'))
            # Redirect to a success page.
        else:
            login_form = LoginForm()
            error_message = 'Wrong password.'
    else:
        login_form = LoginForm()
    return render(request, "portfolio/login4.html", locals())


def create_user(request):
    if request.user.is_authenticated:
        # user already login
        return HttpResponse('你已經登入了')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user = authenticate(username=username, password=password)
        if user is not None:
            # user duplicated
            create_user_form = CreateUserForm()
            error_message = 'User had already exist!'
        else:
            # create user success
            user = User.objects.create_user(username, email, password)
            return redirect('portfolio:login')
    else:
        # if request method isn't POST
        create_user_form = CreateUserForm()

    return render(request, "portfolio/create_user.html", locals())


def create_assets():
    open_df = pd.read_excel("model_result/Omega.xlsx", sheet_name="weight").iloc[:, 1:]
    with connection.cursor() as cursor:
        for assets_name in open_df.columns:
            cursor.execute("insert into portfolio_assets (name) values (%s);", [assets_name])


def get_assets():
    with connection.cursor() as cursor:
        cursor.execute("SELECT name from portfolio_assets;")
        row = cursor.fetchall()
        assets = [x[0] for x in row]
        return assets


def create_index():
    open_df = pd.read_excel("model_result/Omega.xlsx", sheet_name="weight").iloc[:, :]
    with connection.cursor() as cursor:
        for i in open_df.iloc[:, 0]:
            cursor.execute("insert into portfolio_index ('index', period_id) values (%s, %s);", [i + 1, 20 * i + 1])


def create_period():
    open_df = pd.read_excel("model_result/result.xlsx", sheet_name="open").iloc[160:, :]
    with connection.cursor() as cursor:
        for i in open_df.loc[:2000, 'Date'].iloc[:]:
            cursor.execute("insert into portfolio_period (date) values (%s);", [str(i)])


def create_price():
    open_df = pd.read_excel("model_result/result.xlsx", sheet_name="open").iloc[160:, 2:]

    for i in range(93):
        for j in range(466):
            with connection.cursor() as cursor:
                open_df.iloc[20 * i, j]
                cursor.execute("insert into portfolio_price ('price', 'assets_id', 'index_id') values (%s, %s, %s);",
                               [open_df.iloc[20 * i, j], j + 1, i + 1])


def get_period_date():
    with connection.cursor() as cursor:
        cursor.execute(
            "select portfolio_period.date from portfolio_index inner join portfolio_period on portfolio_index.period_id=portfolio_period.id;")
        row = cursor.fetchall()
        period_date = [date[0] for date in row]
        return period_date


def get_prices():
    with connection.cursor() as cursor:
        price_list = []
        for i in range(93):
            cursor.execute("select price from portfolio_price where index_id=%s;", [i + 1])
            row = cursor.fetchall()
            price_list.append([x[0] for x in row])
        return price_list


def get_weight_MV():
    with connection.cursor() as cursor:
        weight_list = []
        for i in range(93):
            cursor.execute("select weight from portfolio_weightmv where index_id=%s;", [i + 1])
            row = cursor.fetchall()
            weight_list.append([x[0] for x in row])
        return weight_list


def get_weight_CVaR():
    with connection.cursor() as cursor:
        weight_list = []
        for i in range(93):
            cursor.execute("select weight from portfolio_weightcvar where index_id=%s;", [i + 1])
            row = cursor.fetchall()
            weight_list.append([x[0] for x in row])
        return weight_list


def get_weight_Omega():
    with connection.cursor() as cursor:
        weight_list = []
        for i in range(93):
            cursor.execute("select weight from portfolio_weightwomega where index_id=%s;", [i + 1])
            row = cursor.fetchall()
            weight_list.append([x[0] for x in row])
        return weight_list


def create_MV_weight():
    open_df = pd.read_excel("model_result/MV.xlsx", sheet_name="weight").iloc[:, 1:]
    for i in range(93):
        for j in range(466):
            with connection.cursor() as cursor:
                cursor.execute(
                    "insert into portfolio_weightmv ('weight', 'assets_id', 'index_id') values (%s, %s, %s);",
                    [float(open_df.iloc[i, j]), j + 1, i + 1])


def create_CVaR_weight():
    open_df = pd.read_excel("model_result/CVaR.xlsx", sheet_name="weight").iloc[:, 1:]
    for i in range(93):
        for j in range(466):
            with connection.cursor() as cursor:
                cursor.execute(
                    "insert into portfolio_weightcvar ('weight', 'assets_id', 'index_id') values (%s, %s, %s);",
                    [float(open_df.iloc[i, j]), j + 1, i + 1])


def create_WOmega_weight():
    open_df = pd.read_excel("model_result/Omega.xlsx", sheet_name="weight").iloc[:, 1:]
    for i in range(93):
        for j in range(466):
            with connection.cursor() as cursor:
                cursor.execute(
                    "insert into portfolio_weightwomega ('weight', 'assets_id', 'index_id') values (%s, %s, %s);",
                    [float(open_df.iloc[i, j]), j + 1, i + 1])


def init_db(request):
    create_assets()
    create_period()
    create_index()
    create_price()
    create_MV_weight()
    create_CVaR_weight()
    create_WOmega_weight()
    return HttpResponse('Complete create all data.')


'''
=================================
'''

# 問卷試算
def questionnaire(request):
    if request.method == "POST":
        question01 = request.POST['question01']
        question02 = request.POST['question02']
        question03 = request.POST['question03']
        question04 = request.POST['question04']
        question05 = request.POST['question05']
        question06 = request.POST['question06']
        question07 = request.POST['question07']
        question08 = request.POST['question08']
        question09 = request.POST['question09']
        question10 = request.POST['question10']
        question11 = request.POST['question11']
        question12 = request.POST['question12']
        amount = int(request.POST['amount'])
        result = [question01,
                  question02,
                  question03,
                  question04,
                  question05,
                  question06,
                  question07,
                  question08,
                  question09,
                  question10,
                  question11,
                  question12, ]
        sharpe_ratio = sum(float(x) for x in result)/12
        # 取得風險偏好與金額，直接做試算
        if sharpe_ratio <= 0.3:
            # cvar
            model_name, top_10_assets_weight_and_name, periods, amount_response, roi = models_CVaR(amount)
        elif sharpe_ratio < 0.7:
            # omega
            model_name, top_10_assets_weight_and_name, periods, amount_response, roi = models_Omega(amount)
        else:
            # mv
            model_name, top_10_assets_weight_and_name, periods, amount_response, roi = models_MV(amount)

        return render(request, "portfolio/Performance.html", locals())
    else:
        # if request method isn't POST
        form = PictureForm()
    return render(request, 'portfolio/Questionnaire.html', locals())


# 投資組合清單
# @login_required
# def portfolio_list(request):
#     user_id = request.user.id
#     # with connection.cursor() as cursor:
#     #     cursor.execute("select risk_preference, amount from portfolio_portfolio where user_id=%s;" % user_id)
#     #     rows = cursor.fetchall()
#     n = [(x, x+1) for x in range(10)]
#     return render(request, 'portfolio/Portfolio_list.html', locals())


# 首頁
def home(request):
    return render(request, 'portfolio/Home.html', locals())


# 會員專區
# @login_required
# def contact(request):
#     user_id = request.user.id
#     with connection.cursor() as cursor:
#         cursor.execute("select risk_preference, amount from portfolio_portfolio where user_id=%s;" % user_id)
#         rows = cursor.fetchall()
#     return HttpResponse(rows)
#     # return render(request, 'portfolio/Contact.html', locals())


# 關於我們
def about(request):
    return render(request, 'portfolio/About.html', locals())


# 用戶註冊
def signUp(request):
    # 用戶已經登入了
    if request.user.is_authenticated:
        return redirect(reverse('portfolio:home'))
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user = authenticate(username=username, password=password)
        try:
            # 註冊成功，登入並導向home
            user = User.objects.create_user(username, email, password)
            login(request, user)
            return redirect(reverse('portfolio:home'))
        except Exception:
            error_message = '用戶名稱重複！'
            return render(request, "portfolio/SingUp.html", locals())
    return render(request, "portfolio/SingUp.html", locals())


# 用戶登入
def signIn(request):
    if request.user.is_authenticated:
        return redirect(reverse('portfolio:home'))

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('portfolio:home'))
        else:
            error_message = '密碼錯誤。'
    else:
        return render(request, "portfolio/SingIn.html", locals())

    return render(request, "portfolio/SingIn.html", locals())


# 用戶登出
def signOut(request):
    logout(request)
    return redirect(reverse('portfolio:home'))


# 快速試算
def calculation(request):
    # 選擇模型跟填入金額 即可試算
    if request.method == "POST":
        model = int(request.POST['model'])
        amount = int(request.POST['amount'])
        '''
        傳送參數amount, 並選取特定之模型function
        '''

        if model == 1:
            model_name, top_10_assets_weight_and_name, periods, amount_response, roi = models_MV(amount)
        elif model == 2:
            model_name, top_10_assets_weight_and_name, periods, amount_response, roi = models_CVaR(amount)
        else:
            model_name, top_10_assets_weight_and_name, periods, amount_response, roi = models_Omega(amount)
    else:
        form = CalculationForm()
        # return render(request, "portfolio/Calculation.html", locals())
        return render(request, "portfolio/Calculation.html", locals())
    return render(request, "portfolio/Performance.html", locals())


def models_MV(amount):
    price = get_prices()
    weight_mv = get_weight_MV()
    amount_mv = {0: amount}
    allocate_mv = {}
    shares_mv = {}
    period = len(weight_mv)
    assets = len(weight_mv[0])
    for i in range(period):
        allocate_mv[i] = [0 for x in range(assets)]
        shares_mv[i] = [0 for x in range(assets)]

        if i != 0:
            amount_mv[i] = sum(price[i][j] * shares_mv[i - 1][j] for j in range(assets))

        for j in range(assets):
            allocate_mv[i][j] = amount_mv[i] * weight_mv[i][j]
            shares_mv[i][j] = allocate_mv[i][j] / price[i][j]

    periods = [date.strftime("%Y/%m/%d") for date in get_period_date()]

    # ROI
    roi = {0: 0.0}
    for i in range(1, period):
        roi[i] = (amount_mv[i] - amount_mv[0]) / amount_mv[0]

    # Annual Return
    amount_response = ["{:.2f}".format(v) for k, v in amount_mv.items()]

    # pie chart
    latest_weight_mv_response = {asset: weight for weight, asset in zip(weight_mv[-1], get_assets())}
    latest_weight_mv_after_sorted = sorted(latest_weight_mv_response.items(), key=lambda x: x[1], reverse=True)
    top_10_assets_name = [x[0] for x in latest_weight_mv_after_sorted[:10]]
    top_10_assets_name.append('Others')
    top_10_assets_weight = [x[1] * 100 for x in latest_weight_mv_after_sorted[:10]]
    top_10_assets_weight.append(sum([x[1] * 100 for x in latest_weight_mv_after_sorted[10:]]))
    top_10_assets_weight_format = ["%.2f" % x for x in top_10_assets_weight]
    top_10_assets_weight_and_name = zip(top_10_assets_name, top_10_assets_weight_format)

    model_name = "MV"
    return model_name, top_10_assets_weight_and_name, periods, amount_response, roi


def models_CVaR(amount):
    price = get_prices()
    weight_CVaR = get_weight_CVaR()
    amount_CVaR = {0: amount}
    allocate_CVaR = {}
    shares_CVaR = {}
    period = len(weight_CVaR)
    assets = len(weight_CVaR[0])
    for i in range(period):
        allocate_CVaR[i] = [0 for x in range(assets)]
        shares_CVaR[i] = [0 for x in range(assets)]

        if i != 0:
            amount_CVaR[i] = sum(price[i][j] * shares_CVaR[i - 1][j] for j in range(assets))

        for j in range(assets):
            allocate_CVaR[i][j] = amount_CVaR[i] * weight_CVaR[i][j]
            shares_CVaR[i][j] = allocate_CVaR[i][j] / price[i][j]

    periods = [date.strftime("%Y/%m/%d") for date in get_period_date()]

    # ROI
    roi = {0: 0.0}
    for i in range(1, period):
        roi[i] = (amount_CVaR[i] - amount_CVaR[0]) / amount_CVaR[0]

    # Annual Return
    amount_response = ["{:.2f}".format(v) for k, v in amount_CVaR.items()]

    # pie chart
    latest_weight_CVaR_response = {asset: weight for weight, asset in zip(weight_CVaR[-1], get_assets())}
    latest_weight_CVaR_after_sorted = sorted(latest_weight_CVaR_response.items(), key=lambda x: x[1], reverse=True)
    top_10_assets_name = [x[0] for x in latest_weight_CVaR_after_sorted[:10]]
    top_10_assets_name.append('Others')
    top_10_assets_weight = [x[1] * 100 for x in latest_weight_CVaR_after_sorted[:10]]
    top_10_assets_weight.append(sum([x[1] * 100 for x in latest_weight_CVaR_after_sorted[10:]]))
    top_10_assets_weight_format = ["%.2f" % x for x in top_10_assets_weight]
    top_10_assets_weight_and_name = zip(top_10_assets_name, top_10_assets_weight_format)

    model_name = "CVaR"

    return model_name, top_10_assets_weight_and_name, periods, amount_response, roi


def models_Omega(amount):
    price = get_prices()
    weight_Omega = get_weight_Omega()
    amount_Omega = {0: amount}
    allocate_Omega = {}
    shares_Omega = {}
    period = len(weight_Omega)
    assets = len(weight_Omega[0])
    for i in range(period):
        allocate_Omega[i] = [0 for x in range(assets)]
        shares_Omega[i] = [0 for x in range(assets)]

        if i != 0:
            amount_Omega[i] = sum(price[i][j] * shares_Omega[i - 1][j] for j in range(assets))

        for j in range(assets):
            allocate_Omega[i][j] = amount_Omega[i] * weight_Omega[i][j]
            shares_Omega[i][j] = allocate_Omega[i][j] / price[i][j]

    periods = [date.strftime("%Y/%m/%d") for date in get_period_date()]

    # ROI
    roi = {0: 0.0}
    for i in range(1, period):
        roi[i] = (amount_Omega[i] - amount_Omega[0]) / amount_Omega[0]

    # Annual Return
    amount_response = ["{:.2f}".format(v) for k, v in amount_Omega.items()]

    # pie chart
    latest_weight_Omega_response = {asset: weight for weight, asset in zip(weight_Omega[-1], get_assets())}
    latest_weight_Omega_after_sorted = sorted(latest_weight_Omega_response.items(), key=lambda x: x[1], reverse=True)
    top_10_assets_name = [x[0] for x in latest_weight_Omega_after_sorted[:10]]
    top_10_assets_name.append('Others')
    top_10_assets_weight = [x[1] * 100 for x in latest_weight_Omega_after_sorted[:10]]
    top_10_assets_weight.append(sum([x[1] * 100 for x in latest_weight_Omega_after_sorted[10:]]))
    top_10_assets_weight_format = ["%.2f" % x for x in top_10_assets_weight]
    top_10_assets_weight_and_name = zip(top_10_assets_name, top_10_assets_weight_format)

    model_name = "Omega"

    return model_name, top_10_assets_weight_and_name, periods, amount_response, roi


# @login_required
# def save_portfolio(request):
#     # get sharpe ratio
#     spr = float(request.POST['spr'])
#     amount = float(request.POST['amt'])
#     user_id = request.user.id
#     with connection.cursor() as cursor:
#         cursor.execute("insert into portfolio_portfolio (risk_preference, amount, user_id) values (%s, %s, %s);" % (spr, amount, user_id))
#     return HttpResponse('數據儲存成功')