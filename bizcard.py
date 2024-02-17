import streamlit as st
import pandas as pd
import numpy as np
import easyocr as ocr
import PIL
from PIL import Image,ImageDraw
import mysql.connector
from streamlit_option_menu import option_menu
import re

#tab1,tab2,tab3=st.tabs(tabs=['Home','Edit Data','Delete Data'])
options=option_menu(None,['Home','Edit Data','Delete Data'])
connection=mysql.connector.connect(host='localhost',user='root',password='Mysql@123',database='db_biz2')
cur=connection.cursor()

#with tab1:
if options=='Home':
    file=st.file_uploader(label='Upload image Here')
    btclick=st.button('Import to Sql')
    reader=ocr.Reader(['en'])
    
    if file:
        img=Image.open(file)
        image=np.array(img)
        image_text=reader.readtext(image)
        text_lst=[i[1] for i in image_text]
        image_copy=img.copy()
        draw=ImageDraw.Draw(image_copy) 

    col1,col2=st.columns(spec=2)

    with col1:
        st.write('Your image')
        if file:
            st.image(file)
            
    with col2:
        st.write('Processed Image')
        if file:
            for i in image_text:
                a,b,c,d=i[0]
                draw.line([*a,*b,*c,*d],fill='red')
            st.image(image_copy)

    if file is not None:


        data = {"company_name": [],
                    "card_holder": [],
                    "designation": [],
                    "mobile_number": [],
                    "email": [],
                    "website": [],
                    "area": [],
                    "city": [],
                    "state": [],
                    "pin_code": [],
                    }


        def get_data(res):
            for ind, i in enumerate(res):
                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4] + "." + res[5]

                # To get EMAIL ID
                elif "@" in i:
                    data["email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) == 2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                # To get COMPANY NAME
                elif ind == len(res) - 1:
                    data["company_name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    data["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+', i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', i):
                    data["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*', i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                if state_match:
                    data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                    data["state"].append(i.split()[-1])
                if len(data["state"]) == 2:
                    data["state"].pop(0)

                # To get PINCODE
                if len(i) >= 6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                    data["pin_code"].append(i[10:])

        get_data(text_lst)

        df=pd.DataFrame(data)

        if btclick:
            for i,rows in df.iterrows():
                query='INSERT INTO card_det VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                cur.execute(query,tuple(rows))
                connection.commit()
                st.success('Data Imported successfully')

#with tab2:
if options=='Edit Data':

        cur.execute('select CardHolderName from card_det;')
        data=cur.fetchall()
        op=[val[0] for val in data]
        op=['None']+op
        selectName=st.selectbox('',op,index=0)

        if selectName=='None':
            st.write('No Card is Selected')

        else:

            cur.execute('SELECT * FROM card_det WHERE CardHolderName=%s',(selectName,))
            resData=cur.fetchone()

            CardHolderName_org=resData[1]   
                
            CompanyName=st.text_input('Company Name',resData[0])
            CardHolderName=st.text_input('Cardholder Name',resData[1])
            Designation=st.text_input('Designation',resData[2])
            MobileNumber=st.text_input('Mobile Number',resData[3])
            Email=st.text_input('Email',resData[4])
            Website=st.text_input('Website',resData[5])
            Area=st.text_input('Area',resData[6])
            City=st.text_input('City',resData[7])
            State=st.text_input('State',resData[8])
            PinCode=st.text_input('Pin Code',resData[9])

            edit_bt=st.button('Edit')
            if edit_bt:
                query='UPDATE card_det SET CompanyName=%s,CardHolderName=%s,Designation=%s,MobileNumber=%s,Email=%s,Website=%s,Area=%s,City=%s,State=%s,PinCode=%s WHERE CardHolderName=%s'
                values=(CompanyName,CardHolderName,Designation,MobileNumber,Email,Website,Area,City,State,PinCode,CardHolderName_org)
                cur.execute(query,values)
                connection.commit()
                st.success('Data modified successfully')
    
            show_bt=st.button('Show Updated Records')

            if show_bt:
                cur.execute('SELECT CompanyName,CardHolderName,Designation,MobileNumber,Email,Website,Area,City,State,PinCode FROM card_det WHERE CardHolderName=%s',(CardHolderName,))
                dataToDisplay=cur.fetchall()
                cl=['CompanyName','CardHolderName','Designation','MobileNumber','Email','Website','Area','City','State','PinCode']
                df=pd.DataFrame(dataToDisplay,columns=cl)
                st.write(df)

if options=='Delete Data':
    cur.execute('select CardHolderName from card_det;')
    data=cur.fetchall()
    op=[val[0] for val in data]
    op=['None']+op
    selectName=st.selectbox('',op,index=0)

    if selectName=='None':
        st.write('No Card is Selected')

    else:
        st.write(f'Selected Card is {selectName}')
        bt=st.button('Proceed to Delete')
        
        if bt:
            cur.execute('DELETE FROM card_det WHERE CardHolderName=%s',(selectName,))
            connection.commit()
            st.success('Record Deleted Successfully')
    bt1=st.button('Display All Records')
    if bt1:
        cur.execute('SELECT CompanyName,CardHolderName,Designation,MobileNumber,Email,Website,Area,City,State,PinCode FROM card_det')
        data=cur.fetchall()
        cl=['CompanyName','CardHolderName','Designation','MobileNumber','Email','Website','Area','City','State','PinCode']
        df=pd.DataFrame(data,columns=cl)
        st.write(df)
