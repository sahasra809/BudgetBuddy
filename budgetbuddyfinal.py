import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client
import pandas as pd
import plotly.express as px
import bcrypt

st.set_page_config(page_title='BudgetBuddy',page_icon='👻',layout='wide',initial_sidebar_state='expanded')

st.markdown("""
<style>
@import url("https://jsdelivr.net");

.features-title{text-align:center;color:white;font-size:34px;font-weight:700;margin-top:25px;}
.features-subtitle{text-align:center;color:#A1A1AA;margin-bottom:30px;}
.feature-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin-top:15px;}
.feature-card{background:#17171D;border:1px solid #2B2B35;border-radius:18px;padding:22px;transition:0.3s;}
.feature-card:hover{transform:translateY(-6px);border:1px solid #8B5CF6;box-shadow:0px 0px 18px rgba(139,92,246,.35);}
.feature-icon{font-size:32px;margin-bottom:8px;}
.feature-title{color:white;font-size:20px;font-weight:600;margin-bottom:8px;}
.feature-desc{color:#A1A1AA;font-size:15px;line-height:1.6;}

.metric-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-top:20px;margin-bottom:30px;}
.metric-card{background:#17171D;border:1px solid #2D2D37;border-radius:22px;padding:22px;transition:.3s;}
.metric-card:hover{transform:translateY(-6px);border-color:#8B5CF6;box-shadow:0 0 22px rgba(139,92,246,.35);}
.metric-icon{font-size:32px;margin-bottom:8px;}
.metric-title{color:#B3B3C2;font-size:16px;}
.metric-value{color:whitefont-size:34px;font-weight:700;margin-top:10px;}

</style>
""", unsafe_allow_html=True)

s_url=st.secrets['SUPABASE_URL']
s_key=st.secrets['SUPABASE_KEY']
supabase=create_client(s_url,s_key)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in=False

if 'user_id' not in st.session_state:
    st.session_state.user_id=None

if 'user_name' not in st.session_state:
    st.session_state.user_name=''

if not st.session_state.logged_in:
    st.markdown("""<h1 style='text-align:center;color:#7DF9FF;margin-bottom:0px;'>👻 BudgetBuddy</h1>
                    <h4 style='text-align:center;color:#A855F7;margin-top:0;'>Track. Analyze. Improve.</h4>"""\
                ,unsafe_allow_html=True)
    st.markdown("""
<div class='features-title'>
Why Us?
</div>

<div class='features-subtitle'>
Everything you need to build smarter financial habits.
</div>

<div class='feature-grid'>

<div class='feature-card'>
<div class='feature-icon'>˗ˋˏ₹ˎˊ˗</div>
<div class='feature-title'>Track Every Expense</div>
<div class='feature-desc'>
Log every purchase in seconds and organize it into categories.
</div>
</div>

<div class='feature-card'>
<div class='feature-icon'>🗐</div>
<div class='feature-title'>Understand Your Spending</div>
<div class='feature-desc'>
Visualize where your money goes with interactive charts and insights.
</div>
</div>

<div class='feature-card'>
<div class='feature-icon'>⌖</div>
<div class='feature-title'>Stay Within Budget</div>
<div class='feature-desc'>
Monitor your monthly budget and avoid overspending.
</div>
</div>

<div class='feature-card'>
<div class='feature-icon'>✦</div>
<div class='feature-title'>Monitor Income</div>
<div class='feature-desc'>
Keep track of every income source alongside your expenses.
</div>
</div>

<div class='feature-card'>
<div class='feature-icon'>🗒</div>
<div class='feature-title'>Financial Reports</div>
<div class='feature-desc'>
Generate summaries and discover spending trends over time.
</div>
</div>

<div class='feature-card'>
<div class='feature-icon'>🔒</div>
<div class='feature-title'>Your Data, Protected</div>
<div class='feature-desc'>
Passwords are securely encrypted using bcrypt before storage.
</div>
</div>

</div>
""", unsafe_allow_html=True)
    
    auth=st.radio('',['Login', 'Signup'],horizontal=True)
    st.markdown('---')

    if auth=='Signup':

        name=st.text_input('Name')
        email=st.text_input('Email')
        email=email.strip().lower()
        password=st.text_input('Password',type='password')
        confirm_password=st.text_input('Confirm Password',type='password')
        budget=st.number_input('Monthly Budget',min_value=0.0,step=100.0)

        if st.button('Create Account'):

            if password!=confirm_password:
                st.error('Passwords do not match!')

            elif len(password)<6:
                st.error('Password must be at least 6 characters!')

            elif not name.strip() or not email.strip():
                st.error('Please fill all fields!')

            else:
                existing=(supabase.table("users").select("email").limit(1).eq("email", email).execute())

                if existing.data:
                    st.error('Email already registered!')

                else:
                    hashed_password = bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()

                    supabase.table('users').insert({'name': name,'email': email,'password': hashed_password,'monthly_budget': budget}).execute()
                    st.balloons()
                    st.success('Account created successfully!')
                    st.info('You can now login.')


    elif auth=='Login': 
        email=st.text_input('Email')
        email=email.strip().lower()
        password=st.text_input('Password',type='password')

        if st.button('Login'):
            response=(supabase.table('users').select('user_id,name,password').eq('email',email).limit(1).execute())

            if response.data:
                user=response.data[0]
                user_id=user['user_id']
                user_name=user['name']
                stored_hash=user['password']

                if bcrypt.checkpw(password.encode(),stored_hash.encode()):
                    st.session_state.logged_in=True
                    st.session_state.user_id=user_id
                    st.session_state.user_name=user_name
                    st.success("Login successful!")
                    st.rerun()

                else:
                    st.error('Incorrect password!')

            else:
                st.error('No account found!')

else:
    st.sidebar.image('cover.jpeg',caption='Make smart financial decisions')

    with st.sidebar:
        menu = option_menu(menu_title=None, options=["Dashboard", "Add Expense", "Add Income", "View Transactions", "Reports", "Profile", "Logout"],
                           icons=["house", "cash-coin", "wallet2", "receipt", "bar-chart-line", "person", "box-arrow-right"],
                           menu_icon="cast", 
                           default_index=0,
                           styles={"container": {"padding": "0!important", "background-color": "transparent"},
                                   "icon": {"color": "#5935bd", "font-size": "16px"}, 
                                   "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
                                   "nav-link-selected": {"background-color": "#9a7ceb"},})

    
    if menu=='Dashboard':
        uid=st.session_state.user_id
        st.title(':material/dashboard: Dashboard')
        st.write(f"Welcome back, {st.session_state.user_name} :material/waving_hand:")
        st.write('Track your income, expenses, and savings at a glance.')

        data=supabase.table('income').select('amount').eq('user_id',uid).execute().data
        total_income=sum(float(i['amount'] or 0) for i in data)

        data=supabase.table('expenses').select('amount').eq('user_id',uid).execute().data
        total_expense=sum(float(i['amount'] or 0) for i in data)

        data=supabase.table('users').select('monthly_budget').eq('user_id',uid).execute().data
        budget=0
        if data:
            budget=float(data[0].get("monthly_budget") or 0)

        savings=total_income-total_expense
        remaining=budget-total_expense

        st.markdown(f"""
        
<div class="metric-grid">

<div class="metric-card">
<div class="metric-icon"><i class="bi bi-cash-stack"></i></div>
<div class="metric-title">Total Income</div>
<div class="metric-value">₹{total_income:,.0f}</div>
</div>

<div class="metric-card">
<div class="metric-icon"><i class="bi bi-credit-card-2-front"></i></div>
<div class="metric-title">Total Expenses</div>
<div class="metric-value">₹{total_expense:,.0f}</div>
</div>

<div class="metric-card">
<div class="metric-icon"><i class="bi bi-crosshair"></i></div>
<div class="metric-title">Budget Left</div>
<div class="metric-value">₹{remaining:,.0f}</div>
</div>

<div class="metric-card">
<div class="metric-icon"><i class="bi bi-graph-up-arrow"></i></div>
<div class="metric-title">Savings</div>
<div class="metric-value">₹{savings:,.0f}</div>
</div>

</div>
""", unsafe_allow_html=True)

        if budget>0:
            percent=(total_expense/budget)*100
            st.progress(min(percent,100)/100)
            st.write(f"{percent:.1f}% of monthly budget used")

            if percent < 50:
                st.success('Great job! Spending is under control :material/star:')

            elif percent < 80:
                st.warning('Budget usage is getting higher :material/visibility:')

            elif percent <= 100:
                st.error("You're close to your budget limit :material/warning:")

            else:
                st.error("You've exceeded your monthly budget! :material/emergency:")

        st.markdown('---')
        st.subheader(':material/pie_chart: Expense Breakdown')

        data=supabase.table('expenses').select('category,amount').eq('user_id',uid).execute().data

        colors={'Food':'#FF6B6B','Transport':'#118AB2','Shopping':'#8338EC','Bills':'#FFD166',\
                'Entertainment':'#FF007F','Education':'#3A86FF','Health':'#06D6A0','Other':'#6C757D'}

        if data:
            df=pd.DataFrame(data)
            df=df.groupby('category',as_index=False)['amount'].sum()
            df.columns=['Category','Amount']

            fig=px.pie(df,names='Category',values='Amount',hole=0.4,color='Category',color_discrete_map=colors)
            fig.update_layout(title='Expense Breakdown By Category')
            st.plotly_chart(fig,use_container_width=True)

        else:
            st.info('No expense data available.')

        st.markdown('---')
        st.subheader(':material/bar_chart: Monthly Expense Trend')

        data=supabase.table('expenses').select('date,amount').eq('user_id',uid).execute().data

        if data:
            df=pd.DataFrame(data)
            df['Month']=pd.to_datetime(df['date']).dt.strftime('%b %Y')
            df=df.groupby('Month',as_index=False)['amount'].sum()
            df.columns=['Month','Expense']
            st.line_chart(df.set_index('Month'))

        else:
            st.info('No monthly trend yet.')

        st.markdown('---')
        st.subheader(':material/lightbulb_outline: Insight')

        data=supabase.table('expenses').select('category,amount').eq('user_id',uid).execute().data

        if data:

            df=pd.DataFrame(data)
            df=df.groupby('category',as_index=False)['amount'].sum()
            top=df.sort_values('amount',ascending=False).iloc[0]

            st.success(f"Your highest spending category is {top['category']} (₹{top['amount']:,.2f})")

            if total_income>0:
                savings_rate=(savings/total_income)*100
                st.info(f":material/money_bag: You saved {savings_rate:.1f}% of your income.")

            budget_left=budget-total_expense

            if budget>0:
                st.info(f":material/my_location: Budget remaining: ₹{budget_left:,.2f}")

            if total_expense>budget and budget>0:
                st.error(':material/warning: You have exceeded your monthly budget!')

            percent=(top['amount']/total_expense)*100
            st.info(f":material/bar_chart: {percent:.1f}% of your expenses were spent on {top['category']}.")

            if savings>0:
                st.success(":material/check_box: You're spending less than you earn!")
            else:
                st.error(':material/warning: Expenses exceed income!')

        else:
            st.info('Start adding expenses to get insights!')


    elif menu=='Add Expense':
        st.title(':material/payments: Add Expense')
        uid=st.session_state.user_id

        data=supabase.table('category').select('category_name').execute().data
        categories=[row['category_name'] for row in data]

        with st.form('expense_form'):
            amount=st.number_input('Amount (₹)',min_value=0.0,step=10.0)
            category=st.selectbox('Category',categories)
            note=st.text_input('Description')
            date=st.date_input('Date')
            submitted=st.form_submit_button('Add Expense')

        if submitted:
            if amount<=0:
                st.error('Amount must be greater than 0')
            else:
                supabase.table('expenses').insert({'user_id':uid,'amount':amount,'category':category,'note':note,'date':str(date)}).execute()
                st.success('Expense added successfully!')
                st.rerun()

        st.markdown('---')
        st.subheader('Recent Expenses')

        data=supabase.table('expenses').select('category,amount,note,date').eq('user_id',uid).order('date',desc=True).limit(5).execute().data

        if data:
            df=pd.DataFrame(data)
            df.columns=['Category','Amount','Note','Date']
            df.index=df.index+1
            st.dataframe(df,use_container_width=True)

        else:
            st.info('No expenses added yet.')

    elif menu=='Add Income':
        st.title(':material/account_balance_wallet: Add Income')
        uid=st.session_state.user_id
        data=supabase.table('income').select('amount').eq('user_id',uid).execute().data
        total_income=sum(float(i['amount'] or 0) for i in data)
        st.metric(':material/money_bag: Total Income',f'₹{total_income:,.2f}')

        with st.form('income_form'):
            amount=st.number_input('Income Amount (₹)',min_value=0.0,step=100.0)
            source=st.selectbox('Source',['Salary','Pocket Money','Freelancing','Gift','Business','Other'])
            date=st.date_input('Date')
            submitted=st.form_submit_button('Add Income')

        if submitted:
            if amount<=0:
                st.error('Amount must be greater than 0!')
            else:
                supabase.table('income').insert({'user_id':uid,'amount':amount,'source':source,'date':str(date)}).execute()
                st.success('Income added successfully!')
                st.rerun()

        st.markdown('---')
        st.subheader('Recent Income')

        data=supabase.table('income').select('source,amount,date').eq('user_id',uid).order('date',desc=True).limit(5).execute().data

        if data:
            df=pd.DataFrame(data)
            df.columns=['Source','Amount','Date']
            df.index=df.index+1
            st.dataframe(df,use_container_width=True)

        else:
            st.info(':material/payments: No income records yet! Start by adding your first expense to see charts and insights.')


    elif menu=='View Transactions':
        st.title(':material/receipt_long: Transaction Ledger')
        uid=st.session_state.user_id
        transaction_type=st.selectbox('Show',['All','Expenses','Income'])

        if transaction_type=='All':
            expense_data=supabase.table('expenses').select('amount,category,note,date').eq('user_id',uid).execute().data
            income_data=supabase.table('income').select('amount,source,date').eq('user_id',uid).execute().data

            expenses=[]
            for i in expense_data:
                expenses.append({'Type':'Expense','Amount':i['amount'],'Details':i['category'],'Note':i['note'],'Date':i['date']})

            incomes=[]
            for i in income_data:
                incomes.append({'Type':'Income','Amount':i['amount'],'Details':i['source'],'Note':'','Date':i['date']})

            data=expenses+incomes

            if data:
                df=pd.DataFrame(data)
                df=df.sort_values('Date',ascending=False)
                df.index=df.index+1
                st.dataframe(df,use_container_width=True)

            else:
                st.info(':material/payments: No transactions yet! Start by adding your first expense to see charts and insights.')

        elif transaction_type=='Expenses':
            data=supabase.table('expenses').select('transaction_id,amount,category,note,date').eq('user_id',uid).order('date',desc=True).execute().data
            df=pd.DataFrame(data)

            if not df.empty:
                df.columns=['ID','Amount','Category','Note','Date']
                df.index=df.index+1
                st.dataframe(df,use_container_width=True,hide_index=True)
                selected_id=st.selectbox('Select expense to delete',df['ID'],format_func=lambda x:f"ID {x} | ₹{df[df['ID']==x]['Amount'].values[0]} | {df[df['ID']==x]['Category'].values[0]}")

                if st.button(':material/delete: Delete Expense',type='primary'):
                    supabase.table('expenses').delete().eq('transaction_id',selected_id).eq('user_id',uid).execute()
                    st.success('Expense deleted successfully!')
                    st.rerun()

            else:
                st.info(':material/payments: No expenses yet! Start by adding your first expense to see charts and insights.')

        elif transaction_type=='Income':
            data=supabase.table('income').select('income_id,amount,source,date').eq('user_id',uid).order('date',desc=True).execute().data
            df=pd.DataFrame(data)

            if not df.empty:
                df.columns=['ID','Amount','Source','Date']
                df.index=df.index+1
                st.dataframe(df,use_container_width=True,hide_index=True)
                selected_id=st.selectbox('Select income to delete',df['ID'],format_func=lambda x:f"ID {x} | ₹{df[df['ID']==x]['Amount'].values[0]} | {df[df['ID']==x]['Source'].values[0]}")

                if st.button(':material/delete: Delete Income',type='primary'):
                    supabase.table('income').delete().eq('income_id',selected_id).eq('user_id',uid).execute()
                    st.success('Income deleted successfully!')
                    st.rerun()

            else:
                st.info(':material/payments: No income records yet! Start by adding your first expense to see charts and insights.')
                

    elif menu=='Reports':
        st.title(':material/bar_chart: Analytics & Summaries')
        report_type=st.selectbox('Select Report',['Monthly Summary','Category Analysis','Income vs Expense',\
                                          'Savings Analysis','Monthly Trend'])
        uid=st.session_state.user_id

        if report_type=='Monthly Summary':
            income_data=supabase.table('income').select('amount').eq('user_id',uid).execute().data
            total_income=sum(float(i['amount'] or 0) for i in income_data)
            expense_data=supabase.table('expenses').select('amount').eq('user_id',uid).execute().data
            total_expense=sum(float(i['amount'] or 0) for i in expense_data)
            savings=total_income-total_expense

            c1,c2,c3=st.columns(3)

            with c1:
                st.metric(':material/money_bag: Income',f'₹{total_income:,.2f}')

            with c2:
                st.metric(':material/payments: Expense',f'₹{total_expense:,.2f}')

            with c3:
                st.metric(':material/account_balance: Savings',f'₹{savings:,.2f}')


        elif report_type=='Category Analysis':
            data=supabase.table('expenses').select('category,amount').eq('user_id',uid).execute().data

            if data:
                df=pd.DataFrame(data)
                df=df.groupby('category',as_index=False)['amount'].sum()
                df.columns=['Category','Amount']
                df.index=df.index+1

                st.dataframe(df,use_container_width=True)

                fig=px.bar(df,x='Category',y='Amount',text='Amount')
                fig.update_layout(title='Category-wise Expenses')
                st.plotly_chart(fig,use_container_width=True)

            else:
                st.info(':material/payments: No expenses yet! Start by adding your first expense to see charts and insights.')


        elif report_type=='Income vs Expense':
            income_data=supabase.table('income').select('amount').eq('user_id',uid).execute().data
            income=sum(float(i['amount'] or 0) for i in income_data)

            expense_data=supabase.table('expenses').select('amount').eq('user_id',uid).execute().data
            expense=sum(float(i['amount'] or 0) for i in expense_data)

            if income and expense:
                df=pd.DataFrame({'Type':['Income','Expense'],'Amount':[income,expense]})

                fig=px.bar(df,x='Type',y='Amount',text='Amount')
                fig.update_layout(title='Income vs Expense Comparison')
                st.plotly_chart(fig,use_container_width=True)

            else:
                print(':material/payments: No data yet! Start by adding your first expense and income to see charts and insights.')


        elif report_type=='Savings Analysis':
            income_data=supabase.table('income').select('amount').eq('user_id',uid).execute().data
            income=sum(float(i['amount'] or 0) for i in income_data)

            expense_data=supabase.table('expenses').select('amount').eq('user_id',uid).execute().data
            expense=sum(float(i['amount'] or 0) for i in expense_data)

            savings=income-expense

            if income>0:
                savings_rate=(savings/income)*100
                st.metric('Savings Rate',f'{savings_rate:.1f}%')
                progress=max(0,min(savings_rate,100)/100)
                st.progress(progress)

                if savings_rate>=30:
                    st.success('Excellent savings habit :material/auto_awesome:')

                elif savings_rate>=10:
                    st.warning('Decent savings. Try improving.')

                else:
                    st.error('Low savings rate.')

            else:
                print(':material/payments: No data yet! Start by adding your first income to see charts and insights.')


        elif report_type=='Monthly Trend':
            data=supabase.table('expenses').select('date,amount').eq('user_id',uid).execute().data

            if data:
                df=pd.DataFrame(data)
                df['Month']=pd.to_datetime(df['date']).dt.strftime('%b %Y')
                df=df.groupby('Month',as_index=False)['amount'].sum()
                df.columns=['Month','Expense']

                fig=px.line(df,x='Month',y='Expense',markers=True)
                fig.update_layout(title='Monthly Spending Trend')
                st.plotly_chart(fig,use_container_width=True)

            else:
                st.info(':material/payments: No expenses yet! Start by adding your first expense to see charts and insights.')
                
    elif menu=='Profile':
        uid=st.session_state.user_id
        st.title(':material/person: Account Settings')

        response=supabase.table('users').select('name,email,monthly_budget,created_at').eq('user_id',uid).execute()

        if not response.data:
            st.error('User not found!')
            st.stop()

        user=response.data[0]
        name=user['name']
        email=user['email']
        budget=float(user['monthly_budget'] or 0)
        created=user['created_at']

        col1,col2=st.columns([1,2])

        with col1:
            st.info(f"Name: {name}")
            st.info(f"Email: {email}")
            st.info(f"Budget: ₹{budget:,.2f}")
            st.info(f"Joined: {created[:10]}")

        income_data=supabase.table('income').select('amount').eq('user_id',uid).execute().data
        total_income=sum(float(i['amount'] or 0) for i in income_data)

        expense_data=supabase.table('expenses').select('amount').eq('user_id',uid).execute().data
        total_expense=sum(float(i['amount'] or 0) for i in expense_data)

        savings=total_income-total_expense

        expense_count=supabase.table('expenses').select('transaction_id').eq('user_id',uid).execute().data
        income_count=supabase.table('income').select('income_id').eq('user_id',uid).execute().data

        transactions=len(expense_count)+len(income_count)

        with col2:

            c1,c2=st.columns(2)

            with c1:
                st.metric(':material/money_bag: Income',f'₹{total_income:,.2f}')
                st.metric(':material/payments: Expense',f'₹{total_expense:,.2f}')

            with c2:
                st.metric(':material/account_balance: Savings',f'₹{savings:,.2f}')
                st.metric(':material/assignment: Transactions',transactions)

        st.markdown('---')
        st.subheader(':material/edit: Edit Profile')

        with st.form('profile_form'):

            new_name=st.text_input('Name',value=name)
            new_budget=st.number_input('Monthly Budget',value=budget)
            update=st.form_submit_button('Update Profile')

            if update:
                if not new_name.strip():
                    st.error('Name cannot be empty!')
                else:
                    supabase.table('users').update({'name':new_name,'monthly_budget':new_budget}).eq('user_id',uid).execute()
                    st.session_state.user_name=new_name
                    st.success('Profile updated successfully!')
                    st.rerun()

        st.markdown('---')
        st.subheader(':material/enhanced_encryption: Change Password')

        with st.form('password_form'):

            old_password=st.text_input('Current Password',type='password')
            new_password=st.text_input('New Password',type='password')
            confirm_password=st.text_input('Confirm New Password',type='password')

            change=st.form_submit_button('Change Password')

            if change:
                if len(new_password)<6:
                    st.error('Password must be at least 6 characters!')

                elif new_password!=confirm_password:
                    st.error('Passwords do not match!')

                elif old_password == new_password:
                    st.error('New password must be different!')

                else:
                    stored_hash=supabase.table('users').select('password').eq('user_id',uid).execute().data[0]['password']

                    if bcrypt.checkpw(old_password.encode(),stored_hash.encode()):
                        new_hash=bcrypt.hashpw(new_password.encode(),bcrypt.gensalt()).decode()
                        supabase.table('users').update({'password':new_hash}).eq('user_id',uid).execute()
                        st.success('Password changed successfully!')
                        st.rerun()

                    else:
                        st.error('Current password is incorrect!')

    delete=st.form_submit_button('Change Password')
    if delete:
        st.warning('Deleting your account will permanently remove your profile, income records, and expense records. This action cannot be undone.')
        confirm_delete=st.checkbox('I understand that this action is permanent.')
        if confirm_delete:
            if st.button(':material/delete: Delete My Account', type='primary'):
                supabase.table('expenses').delete().eq('user_id',uid).execute()
                supabase.table('income').delete().eq('user_id',uid).execute()
                supabase.table('users').delete().eq('user_id',uid).execute()
                st.session_state.logged_in=False
                st.session_state.user_id=None
                st.session_state.user_name=''
                st.success('Your account has been deleted successfully.')
                st.rerun()
        

                                         
    elif menu=='Logout':
        st.session_state.logged_in=False
        st.session_state.user_id=None
        st.session_state.user_name=''
        st.rerun()

st.markdown("---")
st.caption("BudgetBuddy © 2026 | Developed by Pocha Sahasra")
