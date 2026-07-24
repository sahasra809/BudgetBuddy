import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import bcrypt

st.set_page_config(page_title='BudgetBuddy',page_icon='💰',layout='wide')
st.markdown("""
# 💰 BudgetBuddy  
### Track. Analyze. Improve your spending.

---
""")

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
    st.image('front.jpeg')
    auth = st.radio('',['Login', 'Signup'],horizontal=True)
    st.markdown('---')

    if auth=='Signup':
        st.subheader('📝 Create Account')

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

                    supabase.table("users").insert({"name": name,"email": email,"password": hashed_password,"monthly_budget": budget}).execute()
                    st.balloons()
                    st.success("Account created successfully!")
                    st.info("You can now login.")


    elif auth=='Login':
        st.subheader('🔐 Login')
        email=st.text_input('Email')
        email=email.strip().lower()
        password=st.text_input('Password', type='password')

        if st.button('Login'):
            response=(supabase.table("users").select("user_id,name,password").eq("email",email).limit(1).execute())

            if response.data:
                user=response.data[0]
                user_id=user["user_id"]
                user_name=user["name"]
                stored_hash=user["password"]

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
    menu=st.sidebar.selectbox('Menu',['🏠 Dashboard','💸 Add Expense','💵 Add Income','📋 View Transactions',\
                                      '📊 Reports','👤 Profile','🚪 Logout'])

    if menu=='🏠 Dashboard':
        uid=st.session_state.user_id
        st.title('🏠 Dashboard')
        st.write(f"Welcome back, {st.session_state.user_name}👋")
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

        col1,col2,col3,col4,col5=st.columns(5)

        with col1:
            st.metric('💵 Income',f'₹{total_income:,.2f}')

        with col2:
            st.metric('💸 Expenses',f'₹{total_expense:,.2f}')

        with col3:
            st.metric('💰 Savings',f'₹{savings:,.2f}')

        with col4:
            st.metric('🎯 Budget',f'₹{budget:,.2f}')
            
        with col5:
            remaining=budget-total_expense
            if remaining>=0:
                st.metric("🎯 Budget Left",f"₹{remaining:,.2f}")
            else:
                st.metric("⚠️ Over Budget",f"₹{abs(remaining):,.2f}")

        st.markdown('---')
        st.subheader('📊 Budget Usage')

        if budget>0:
            percent=(total_expense/budget)*100
            st.progress(min(percent,100)/100)
            st.write(f"{percent:.1f}% of monthly budget used")

            if percent < 50:
                st.success('Great job! Spending is under control 🌟')

            elif percent < 80:
                st.warning('Budget usage is getting higher 👀')

            elif percent <= 100:
                st.error("You're close to your budget limit ⚠️")

            else:
                st.error("You've exceeded your monthly budget! 🚨")

        st.markdown('---')
        st.subheader('🥧 Expense Breakdown')

        data=supabase.table('expenses').select('category,amount').eq('user_id',uid).execute().data

        colors={'Food':'#EC7D7E','Transport':'#6A36BC','Shopping':'#1395BA','Bills':'#7F8000',\
                'Entertainment':'#E5A90C','Education':'#4EAED4','Health':'#2ECA71','Other':'#95A2A6'}

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
        st.subheader('📈 Monthly Expense Trend')

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
        st.subheader('💡 Insight')

        data=supabase.table('expenses').select('category,amount').eq('user_id',uid).execute().data

        if data:

            df=pd.DataFrame(data)
            df=df.groupby('category',as_index=False)['amount'].sum()
            top=df.sort_values('amount',ascending=False).iloc[0]

            st.success(f"Your highest spending category is {top['category']} (₹{top['amount']:,.2f})")

            if total_income>0:
                savings_rate=(savings/total_income)*100
                st.info(f"💰 You saved {savings_rate:.1f}% of your income.")

            budget_left=budget-total_expense

            if budget>0:
                st.info(f"🎯 Budget remaining: ₹{budget_left:,.2f}")

            if total_expense>budget and budget>0:
                st.error('⚠️ You have exceeded your monthly budget!')

            percent=(top['amount']/total_expense)*100
            st.info(f"📊 {percent:.1f}% of your expenses were spent on {top['category']}.")

            if savings>0:
                st.success("✅ You're spending less than you earn!")
            else:
                st.error('⚠️ Expenses exceed income!')

        else:
            st.info('Start adding expenses to get insights!')


    elif menu=='💸 Add Expense':
        st.title('💸 Add Expense')
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

    elif menu=='💵 Add Income':
        st.title('💵 Add Income')
        uid=st.session_state.user_id
        data=supabase.table('income').select('amount').eq('user_id',uid).execute().data
        total_income=sum(float(i['amount'] or 0) for i in data)
        st.metric('💰 Total Income',f'₹{total_income:,.2f}')

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
            st.info('💸 No income records yet! Start by adding your first expense to see charts and insights.')


    elif menu=='📋 View Transactions':
        st.title('📋 Transactions')
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
                st.info('💸 No transactions yet! Start by adding your first expense to see charts and insights.')

        elif transaction_type=='Expenses':
            data=supabase.table('expenses').select('transaction_id,amount,category,note,date').eq('user_id',uid).order('date',desc=True).execute().data
            df=pd.DataFrame(data)

            if not df.empty:
                df.columns=['ID','Amount','Category','Note','Date']
                df.index=df.index+1
                st.dataframe(df,use_container_width=True,hide_index=True)
                selected_id=st.selectbox('Select expense to delete',df['ID'],format_func=lambda x:f"ID {x} | ₹{df[df['ID']==x]['Amount'].values[0]} | {df[df['ID']==x]['Category'].values[0]}")

                if st.button('🗑 Delete Expense',type='primary'):
                    supabase.table('expenses').delete().eq('transaction_id',selected_id).eq('user_id',uid).execute()
                    st.success('Expense deleted successfully!')
                    st.rerun()

            else:
                st.info('💸 No expenses yet! Start by adding your first expense to see charts and insights.')

        elif transaction_type=='Income':
            data=supabase.table('income').select('income_id,amount,source,date').eq('user_id',uid).order('date',desc=True).execute().data
            df=pd.DataFrame(data)

            if not df.empty:
                df.columns=['ID','Amount','Source','Date']
                df.index=df.index+1
                st.dataframe(df,use_container_width=True,hide_index=True)
                selected_id=st.selectbox('Select income to delete',df['ID'],format_func=lambda x:f"ID {x} | ₹{df[df['ID']==x]['Amount'].values[0]} | {df[df['ID']==x]['Source'].values[0]}")

                if st.button('🗑 Delete Income',type='primary'):
                    supabase.table('income').delete().eq('income_id',selected_id).eq('user_id',uid).execute()
                    st.success('Income deleted successfully!')
                    st.rerun()

            else:
                st.info('💸 No income records yet! Start by adding your first expense to see charts and insights.')
                

    elif menu=='📊 Reports':
        st.title('📊 Financial Reports')
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
                st.metric('💰 Income',f'₹{total_income:,.2f}')

            with c2:
                st.metric('💸 Expense',f'₹{total_expense:,.2f}')

            with c3:
                st.metric('🏦 Savings',f'₹{savings:,.2f}')


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
                st.info('💸 No expenses yet! Start by adding your first expense to see charts and insights.')


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
                st.info('💸 No data yet! Start by adding your first expense and income to see charts and insights.')


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
                    st.success('Excellent savings habit 🌟')

                elif savings_rate>=10:
                    st.warning('Decent savings. Try improving.')

                else:
                    st.error('Low savings rate.')

            else:
                st.info('💸 No data yet! Start by adding your first income to see charts and insights.')


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
                st.info('💸 No expenses yet! Start by adding your first expense to see charts and insights.')
                
    elif menu=='👤 Profile':
        uid=st.session_state.user_id
        st.title('👤 My Profile')

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
                st.metric('💰 Income',f'₹{total_income:,.2f}')
                st.metric('💸 Expense',f'₹{total_expense:,.2f}')

            with c2:
                st.metric('🏦 Savings',f'₹{savings:,.2f}')
                st.metric('📋 Transactions',transactions)

        st.markdown('---')
        st.subheader('✏️ Edit Profile')

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
        st.subheader('🔐 Change Password')

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
                        
        st.warning('Deleting your account will permanently remove your profile, income records, and expense records. This action cannot be undone.')
        confirm_delete=st.checkbox('I understand that this action is permanent.')
        
        if confirm_delete:
            if st.button('🗑 Delete My Account', type='primary'):
                supabase.table('expenses').delete().eq('user_id',uid).execute()
                supabase.table('income').delete().eq('user_id',uid).execute()
                supabase.table('users').delete().eq('user_id',uid).execute()
                st.session_state.logged_in=False
                st.session_state.user_id=None
                st.session_state.user_name=''
                st.success('Your account has been deleted successfully.')
                st.rerun()

                                         
    elif menu=='🚪 Logout':
        st.session_state.logged_in=False
        st.session_state.user_id=None
        st.session_state.user_name=''
        st.rerun()

st.markdown("---")
st.caption("BudgetBuddy © 2026 | Developed by Pocha Sahasra")
