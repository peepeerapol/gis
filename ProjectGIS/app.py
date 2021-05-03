from flask import Flask, render_template,url_for,request,redirect,jsonify,Response
from flask_wtf import FlaskForm 
from wtforms import TextField,SubmitField,BooleanField,RadioField,SelectField,TextAreaField 
from wtforms.validators import DataRequired
import pyodbc
import pandas as pd
import json
import xlwt
import io

app = Flask(__name__)

SQLSERVER = 'DESKTOP-4KLR06G'
SQLDB = 'SpatialDB'
str_conn = 'Driver={SQL Server};Server=%s;Database=%s;Trusted_Connection=yes;'%(SQLSERVER, SQLDB)
conn = pyodbc.connect(str_conn)

cursor = conn.cursor()

@app.route('/index',methods=['GET'])
def index():
   cursor = conn.cursor()
   cursor.execute('SELECT * FROM dbo.AirPollutionPM25')
   rows = cursor.fetchall()
   return render_template('index.html',r = rows)

@app.route('/')
def home():
   return render_template('HOME.html')


@app.route('/delete/<county>/<city>/<years>/<latitude>/<longitude>',methods=['GET'])
def delete(county,city,years,latitude,longitude):
    if request.method == "GET" :        
      with conn.cursor() as cursor:
        cursor.execute("DELETE FROM dbo.AirPollutionPM25 where county=? AND city=? AND years=? AND latitude=? AND longitude=? ",(county,city,years,latitude,longitude))
        conn.commit()
        return redirect(url_for('index'))
 
@app.route('/add', methods = ['POST','GET'])
def add():
   if request.method == "POST" :
       
       county = request.form['county']
       city = request.form['city']
       latitude = float(request.form['latitude'])
       longitude = float(request.form['longitude'])
       years = int(request.form['years'])
       populations = int(request.form['populations'])
       wbinc16_text =request.form['wbinc16_text']
       region = request.form['region']
       pm25 = float(request.form['pm25'])
       color_pm25 = '-'
       conc_pm25 = '-'    
       if(pm25<=10):
         color_pm25 = 'green'  
         conc_pm25 = '<10'
       elif(10<pm25<=15):
         color_pm25 = 'yellow' 
         conc_pm25 = '10-<15'
       elif(15<pm25<=25):
         color_pm25 = 'orange' 
         conc_pm25 = '15-<25'
       elif(25<pm25<=35):
         color_pm25 = 'darkorange' 
         conc_pm25 = '25-<35'
       elif(35<pm25<=50): 
         color_pm25 = 'red' 
         conc_pm25 = '35-<50'
       else:
         color_pm25 = 'darkred' 
         conc_pm25 = '>50'
       with conn.cursor() as cursor:
              sql = "Insert into dbo.AirPollutionPM25(county,city,years,pm25,latitude,longitude,populations,wbinc16_text,region,conc_pm25,color_pm25) values(?,?,?,?,?,?,?,?,?,?,?)"
              cursor.execute(sql,(county,city,years,pm25,latitude,longitude,populations,wbinc16_text,region,conc_pm25,color_pm25))
              conn.commit()
              return redirect(url_for('index'))

@app.route('/historical')
def historical():
   return render_template('historical.html')


@app.route('/cal_historical', methods = ['POST'])
def cal_historical():
   if request.method == "POST" :     
      county = request.form['county']
      sql = "SELECT pm25,city,years FROM dbo.AirPollutionPM25 WHERE county = ? ORDER BY years,city"
   with conn.cursor() as cursor:
      cursor.execute(sql,(county))
      table = cursor.fetchall()

      output = io.BytesIO()
      workbook = xlwt.Workbook()
      sh = workbook.add_sheet('Data Report')

      sh.write(0,0,'pm25')
      sh.write(0,1,'city')
      sh.write(0,2,'years')

      idx = 0
      for row in table:
            sh.write(idx+1,0, row[0])
            sh.write(idx+1,1, row[1])
            sh.write(idx+1,2, row[2])

            idx += 1
      workbook.save(output)
      output.seek(0)         
      return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=HistoricalPM25_Report.xls"})
      return redirect(url_for('historical.html'))

@app.route('/affected')
def affected():
   return render_template('affected.html')

@app.route('/cal_affected', methods = ['POST'])
def cal_affected():
   if request.method == "POST" : 
      years = int(request.form['years'])
      color_pm25 = request.form['color_pm25'] 
      sql = "SELECT SUM(populations) as total_pop FROM dbo.AirPollutionPM25 WHERE years =? AND color_pm25 = ? "
   with conn.cursor() as cursor:
      cursor.execute(sql,(years,color_pm25))
      mydata = cursor.fetchall()

      output = io.BytesIO()
      workbook = xlwt.Workbook()
      sh = workbook.add_sheet('Data Report')

      sh.write(0,0,'total of the affected')

      idx = 0
      for row in mydata:
            sh.write(idx+1,0, row[0])
            idx += 1
      workbook.save(output)
      output.seek(0)         
      return Response (output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=Data_Report.xls"})
   return redirect('affected.html')


@app.route('/insertCSV', methods = ['POST'] )
def insertCSV():  
   if request.method == "POST" : 
      filecsv = request.form['filecsv']
      data = pd.read_csv(r'%s'% filecsv)

      df = pd.DataFrame(data ,columns = ['country','city','years','pm25',
                                         'latitude','longitude','populations','wbinc16_text',
                                         'Region','conc_pm25','color_pm25'])
   with conn.cursor() as cursor:
      for row in df.itertuples():

          latitude = float(row.latitude)
          longitude = float(row.longitude)
          pm25 = float(row.pm25)
          years = int(row.years)
          populations = int(row.populations)
    
          cursor.execute( "INSERT INTO dbo.AirPollutionPM25(county,city,years,pm25,latitude,longitude,populations,wbinc16_text,Region,conc_pm25,color_pm25) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(row.country,row.city,years,pm25,latitude,longitude,populations,row.wbinc16_text,row.Region,row.conc_pm25,row.color_pm25))
          conn.commit()
      conn.commit()
      return redirect(url_for('index'))


@app.route('/allcountries')
def allcountries():
    return render_template('allcountries.html')

@app.route('/citylowcome')
def citylowcome():
    return render_template('income.html')

@app.route('/citypoints', methods = ['POST'])
def citypoints():
   if request.method == "POST" : 
        years = int(request.form['years'])
        tiltlegm = 'The city points of all Countries in '
        with conn.cursor() as cursor:
           cursor.execute('SELECT county,city,pm25,latitude,longitude FROM dbo.AirPollutionPM25 WHERE years = ? for JSON PATH ' ,(years))
           mydata = cursor.fetchall()
           cursor.execute('SELECT count(*) FROM dbo.AirPollutionPM25 WHERE years = ?  ' ,(years))
           countdata = cursor.fetchall()
           jsonn = ""

           for row in countdata:
              count = row[0]

           for row in mydata:
              jsonn = jsonn + row[0]
           return render_template('map.html',jsonn = jsonn,year = years,tiltle = tiltlegm ,count = count)

@app.route('/income', methods = ['POST'])
def income():
   if request.method == "POST" : 
        years = int(request.form['years'])
        tiltleimcome = 'The city points of all Countries in '
        with conn.cursor() as cursor:
           cursor.execute("SELECT county,city,pm25,latitude,longitude FROM dbo.AirPollutionPM25 WHERE years = ? AND wbinc16_text = 'Low income' for JSON PATH " ,(years))
           mydata = cursor.fetchall()
           cursor.execute("SELECT count(*) FROM dbo.AirPollutionPM25 WHERE years = ? AND wbinc16_text = 'Low income' " ,(years))
           countdata = cursor.fetchall()
           jsonn = ""

           for row in countdata:
              count = row[0]
      
           for row in mydata:
              jsonn = jsonn + row[0]
           return render_template('polyline.html',jsonn = jsonn, tiltle = tiltleimcome ,year = years,count = count)
    
@app.route('/closestcity')
def closestcity(): 
        tiltleclosestcity = 'the 50 closest city points to Bangkok '
        cursor = conn.cursor()
        sql = "SELECT TOP 50 county,city,pm25,latitude,longitude, Distance FROM (SELECT county ,city,pm25,latitude,longitude, (ABS(NL.Latitude - 13.74622118) + ABS(NL.Longitude - 100.5544779)) / 2  as Distance FROM AirPollutionPM25 AS NL WHERE (NL.Latitude IS NOT NULL) AND (NL.Longitude IS NOT NULL) AND city != 'Bangkok') AS D1 ORDER BY Distance for JSON PATH "
        cursor.execute(sql)
        mydata = cursor.fetchall()
        countdata = '50'
        jsonn = ""
        for row in mydata:
          jsonn = jsonn + row[0]
        return render_template('map.html',jsonn = jsonn, tiltle = tiltleclosestcity,count = countdata )

@app.route('/highestno')
def highestno(): 
        tiltlehighestno = 'City points of countries having the highest no in 2011'
        cursor = conn.cursor()
        sql = "select county,city,pm25,latitude,longitude,years FROM dbo.AirPollutionPM25 WHERE county in(select county FROM dbo.AirPollutionPM25 WHERE years = 2011 AND pm25 in ( select Max(pm25) FROM dbo.AirPollutionPM25 where years = 2011)) order by pm25 desc for JSON PATH "
        cursor.execute(sql)
        mydata = cursor.fetchall()
        jsonn = ""
        for row in mydata:
          jsonn = jsonn + row[0]
        return render_template('map2.html',jsonn = jsonn, tiltle = tiltlehighestno)

@app.route('/MBR')
def MBR(): 
        tiltlehighestno = 'MBR covering all city points in Thailand in 2014'
        cursor = conn.cursor()
        sql = "select city,pm25,latitude,longitude,years from dbo.AirPollutionPM25 where county = 'Thailand' and years = 2014 for JSON PATH "
        cursor.execute(sql)
        mydata = cursor.fetchall()
        jsonn = ""
        for row in mydata:
          jsonn = jsonn + row[0]
        return render_template('polyline.html',jsonn = jsonn, tiltle = tiltlehighestno)

@app.route('/neighboring')
def neighboring(): 
        tiltle = 'the city points of Thailand’s neighboring '
        cursor = conn.cursor()
        #sql = "select city,pm25,latitude,longitude,years from AirPollutionPM25 as a where a.county in ('Thailand') AND a.years = 2016 for JSON PATH "
        sql = "SELECT TOP 40 county,city,pm25,latitude,longitude, Distance FROM (SELECT county ,city,pm25,latitude,longitude, (ABS(NL.Latitude - 13.74622118) + ABS(NL.Longitude - 100.5544779)) / 2  as Distance FROM AirPollutionPM25 AS NL WHERE (NL.Latitude IS NOT NULL) AND (NL.Longitude IS NOT NULL) AND county != 'Thailand') AS D1  ORDER BY Distance for JSON PATH"
        cursor.execute(sql)
        mydata = cursor.fetchall()
        jsonn = ""
        for row in mydata:
           jsonn = jsonn + row[0]
        return render_template('map3.html',jsonn = jsonn, tiltle = tiltle)

@app.route('/pmgreater')
def pmgreater():
   return render_template('pmgreater.html')

@app.route('/cal_pmgreater')
def cal_pmgreater ():
      with conn.cursor() as cursor:
         cursor.execute("SELECT county,city FROM dbo.AirPollutionPM25 WHERE pm25 > 50 AND years = 2015 ORDER BY county")
         mydata = cursor.fetchall()

      output = io.BytesIO()
      workbook = xlwt.Workbook()
      sh = workbook.add_sheet('PM25more50in2015')

      sh.write(0,0,'country')
      sh.write(0,1,'city')

      idx = 0
      for row in mydata:
            sh.write(idx+1,0, row[0])
            sh.write(idx+1,1, row[1])
            idx += 1
      workbook.save(output)
      output.seek(0)         
      return Response (output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=PM25more50in2015.xls"})
      return redirect('pmgreater.html')


@app.route('/cal_avg')
def cal_avg ():
      with conn.cursor() as cursor:
         cursor.execute("SELECT county, AVG(pm25) AS AVGpm25 FROM dbo.AirPollutionPM25 Group by county ORDER by AVGpm25 DESC")
         mydata = cursor.fetchall()

      output = io.BytesIO()
      workbook = xlwt.Workbook()
      sh = workbook.add_sheet('AVGpm25')

      sh.write(0,0,'country')
      sh.write(0,1,'AVGpm25')

      idx = 0
      for row in mydata:
            sh.write(idx+1,0, row[0])
            sh.write(idx+1,1, row[1])
            idx += 1
      workbook.save(output)
      output.seek(0)         
      return Response (output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=AVGpm25.xls"})
      return redirect('pmgreater.html')

if __name__ == '__main__':
   app.run(debug = True)