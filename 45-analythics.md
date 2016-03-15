##Аналитическая обработка данных

В этой части проекта необходимо выполнить статистическую обработу получяемых данных. Для реализации этого потребуется реализровать следующие компоненты инфраструктуры:
- В платформе Bluemix реализовать сервис хранения данных в БД dashDB. 
- Разработать структуру таблиц базы данных и SQL скрипты для добавления новых данных и удаления устаревших данных.
- Разработать поток Node-Red, реализующий запуск SQL скриптов. 
- Выполнить проверку работоспособности потока с использованием консоли административной косноли dashDB.
- Выполнить разработку аналитического скрипта на языке R в среде RStudio.
- Разработать потока обработки Node-Red для запуска R скрипта.	

Дополнительная информация: 

[Язык программирования R](https://ru.wikibooks.org/wiki/%D0%AF%D0%B7%D1%8B%D0%BA_%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F_R)

[Краткая справка по командам языка R](https://cran.r-project.org/doc/contrib/Short-refcard.pdf)

[Описание IDE RStudio](http://r-analytics.blogspot.ru/p/rstudio.html#.VuiE7x_fVNA)

[Инструкции определения данных на языке DDL](https://msdn.microsoft.com/ru-ru/library/cc879262%28v=sql.120%29.aspx)

[Краткий справочник по командам SQL](http://4its.ru/html/sql-commands.html)


###Работа с сервисом dashDB

К началу этапа рабочая область проекта представляет собой три взаимосвязанных компонента:
- Сервис IoT Foundation для реализации функций брокера MQTT
- Сервис CloudantDB для хранения настроек  IoT Foundation и Node-Red.
- Приложения JavaScript в Node-Red сервере приложений.

![Рабочая область проекта](assets/analythics01.png)

Сервис dashDB представляет собой интегрированные компоненты для реализации функций хранения и аналитической обработки данных с помощью языка R. Сервис позволяет создавать и контролировать состояние SQL базы данных dashDB, содержит набор готовых скриптов на языке R, позволяет создавать и отлаживать пользовательские скрипты.

####Добавление сервиса в проект
Выполним добавление сервиса dashDB. 
На вкладке Catalog в секции Data and Analythics необходимо выбрать сервис dashDB.

![Добавление сервиса dashDB](assets/analythics02.png)

В следующем окне вводятся поля Dev, App, Service. Все поля кроме App можно оставить без изменений. В поле App в выпадающем списке выберете имя вашего приложения Node-Red. Cвязывание позволит выполнять обращения к dashDB со стороны приложений Node-Red (можно выполнить связывание позднее).

![Связывание dashDB с приложением Node-Red](assets/analythics03.png)

Нажмите кнопку Create. После создания сервиса появится возможность перейти в консоль управления. Для этого нажмите на кнопку Launch.

![Консоль управления dashDB](assets/analythics04.png)

Для работы с сервисом необходимо определить параметры: User ID, Host name, Password, Port number. Указанная информация доступна на владке Connect в пункте Connect Information. Указанная информация понадобится впоследствии. 

![Параметры для подключения к сервису dashDB](assets/analythics05.png)


####Создание таблиц

На вкладке Tables объединены функции управления структурой базы данных. При создании сервиса автоматически создается новая база с именем, совпадающим в полем User ID (в примере: DASH105325).

Добавим в базу две таблицы:

- Таблица SOURCE для хранения первичных данных от датчиков.
- Таблица ANALYTHIC для хранения данных предиктивной аналитики.
- Таблица MIXED для хранения первичных данных и предиктивной аналитики.

Для этого необходимо выбрать пункт Add Table и в открывшемся окне ввести код DDL.

Для создания таблицы SOURCE

```SQL
CREATE TABLE "SOURCE" 
(
  "ID" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
  "TEMP" DOUBLE,
  "ANGLE" DOUBLE,
  "TS" TIMESTAMP,
  PRIMARY KEY(ID)
);
```

Для создания таблицы ANALYTHIC

```SQL
CREATE TABLE "ANALYTHIC" 
(
  "ID" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
  "PREDICTTEMP" DOUBLE,
  "PREDICTANGLE" DOUBLE,
  "TS" TIMESTAMP,
  PRIMARY KEY(ID)
);
```

Для создания таблицы MIXED

```SQL
CREATE TABLE "MIXED" 
(
  "ID" INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1, NO CACHE ),
  "PREDICTTEMP" DOUBLE,
  "PREDICTANGLE" DOUBLE,
  "TEMP" DOUBLE,
  "ANGLE" DOUBLE,
  "TS" TIMESTAMP,
  PRIMARY KEY(ID)
);
```

Поле TS предусмотрено для хранения метки времени. 
Ключевое поле ID содержит автоинкрементное значение номера записи (необходимо для отсчета значений в скриптах R и построения графиков). 

####Запуск потоковой записи первичных данных.

В приложении Node-Red необходимо связать блок IoT Foundation с функциональными блоким, формирующими структуру объекта payload, после чего прередать его в блок "dashDB out node". В блоке dashDB указать поле Service dashDB-xx (название сервиса dashDB).


```json
[{"id":"7562821a.8a9d7c","type":"ibmiot in","z":"464be866.b9b418","authentication":"quickstart","apiKey":"","inputType":"evt","deviceId":"93d7da18e689","applicationId":"","deviceType":"+","eventType":"+","commandType":"","format":"json","name":"IBM IoT App In","service":"quickstart","allDevices":false,"allApplications":false,"allDeviceTypes":true,"allEvents":true,"allCommands":false,"allFormats":false,"x":184,"y":320,"wires":[["410e7525.bef18c","522c279c.add3d8"]]},{"id":"410e7525.bef18c","type":"function","z":"464be866.b9b418","name":"iot_db","func":"var interval = (1000*5); // minimum interval between messages (ms)\ncontext.lastTime = context.lastTime || 0;\n\nvar now = Date.now();\n\nif (now-context.lastTime < interval) {\n  return null;\n} \nelse\n{\n    context.lastTime = now;\n    msg.payload =\n    {\n        TS : 'TIMESTAMP',\n        TEMP : msg.payload.d.temp,\n        ANGLE : msg.payload.d.angle\n    }\n    return msg;\n}\n","outputs":1,"noerr":0,"x":478,"y":256.5,"wires":[["46a5a421.b95a5c"]]},{"id":"46a5a421.b95a5c","type":"dashDB out","z":"464be866.b9b418","service":"dashDB-nx","table":"SOURCE","name":"SAVE SOURCE","x":714,"y":256,"wires":[]},{"id":"522c279c.add3d8","type":"function","z":"464be866.b9b418","name":"iot_db","func":"var interval = (1000*5); // minimum interval between messages (ms)\ncontext.lastTime = context.lastTime || 0;\n\nvar now = Date.now();\n\nif (now-context.lastTime < interval) {\n  return null;\n} \nelse\n{\n    context.lastTime = now;\n    msg.payload =\n    {\n        TS : 'TIMESTAMP',\n        TEMP : msg.payload.d.temp,\n        ANGLE : msg.payload.d.angle,\n        PREDICTTEMP : null,\n        PREDICTANGLE : null\n    }\n    return msg;\n}\n","outputs":1,"noerr":0,"x":474,"y":399,"wires":[["1b11131.fe4eeed"]]},{"id":"1b11131.fe4eeed","type":"dashDB out","z":"464be866.b9b418","service":"dashDB-nx","table":"MIXED","name":"SAVE MIXED","x":711,"y":399,"wires":[]},{"id":"250de2a4.daf21e","type":"comment","z":"464be866.b9b418","name":"Добавление данных в таблицу SOURCE","info":"Добавление данных в таблицу SOURCE","x":609,"y":221,"wires":[]},{"id":"b62334a4.49dcc8","type":"comment","z":"464be866.b9b418","name":"Добавление данных в таблицу MIXED","info":"Добавление данных в таблицу MIXED","x":603,"y":358,"wires":[]}]
```

***Примечание: для вставки кода потока в Node-Red в правом вурхнем углу выберите пункт Import и далее пункт Clipboard. Скопируйте код в открывшееся окно и нажмите OK.***



![Поток обработки для записи данных в dashDB](assets/analythics06.png)


Обратите внимание, что в функциональных блоках название ключей в структуре payload должно совпадать с полями таблицы базы данных.

Например:

```js
    msg.payload =
    {
        TS : 'TIMESTAMP',
        TEMP : msg.payload.d.temp,
        ANGLE : msg.payload.d.humidity,
        PREDICTTEMP : null,
        PREDICTANGLE : null

    }
    return msg; 
```

Проверим работоспособность приложения (кнопка Deploy). В консоли управления dashDB на вкладе Tables выберете таблицу SOURCE и Browse Data.
Данные от сенсоров должны быть выбаны на экран. 

![Проверка работоспособности скриптов SQL в консоли dashDB](assets/analythics07.png)


####Удаление данных из таблиц

Все полученные данные накапливаются в таблицах SOURCE,ANALYTHIC и MIXED. Так как время аналитической обработки зависит от объемов данных, выпролним удаление устаревших строк из таблиц. Для этого добавим следующий поток обработки, содержащий SQL скрипты

```json
[{"id":"ed3191e1.12ce7","type":"inject","z":"464be866.b9b418","name":"Clear table","topic":"","payload":"","payloadType":"date","repeat":"30","crontab":"","once":true,"x":319,"y":629,"wires":[["3a10c273.c5ef3e","c2da84ed.3d2578","fc00c702.03ff38"]]},{"id":"3a10c273.c5ef3e","type":"dashDB in","z":"464be866.b9b418","service":"dashDB-nx","query":"DELETE FROM SOURCE WHERE ID<=(SELECT max(ID) FROM SOURCE)-200;","params":"","name":"DLELETE OLD from SOURCE","x":607,"y":572.5,"wires":[[]]},{"id":"eb53b616.14ac48","type":"comment","z":"464be866.b9b418","name":"Удаление старых данных","info":"Удаление старых данных","x":526,"y":526,"wires":[]},{"id":"c2da84ed.3d2578","type":"dashDB in","z":"464be866.b9b418","service":"dashDB-nx","query":"DELETE FROM ANALYTHIC WHERE ID<=(SELECT max(ID) FROM ANALYTHIC)-200;","params":"","name":"DLELETE OLD from ANALYTHIC","x":614,"y":642,"wires":[[]]},{"id":"fc00c702.03ff38","type":"dashDB in","z":"464be866.b9b418","service":"dashDB-nx","query":"DELETE FROM MIXED WHERE ID<=(SELECT max(ID) FROM MIXED)-200;","params":"","name":"DLELETE OLD from MIXED","x":597,"y":710,"wires":[[]]}]
```

![Удаление устаревших данных из таблиц dashDB](assets/analythics075.png)



####Создание скрипта в Rstudio

В консоли dashDB перейти в пунтк Analythics и далее R Scripts. 
Выбрать пункт RStudio. 

![Ввод User ID и Password для входа в RStudio](assets/analythics08.png)

В результате будет открыто окно RStudio, в котором может выполняться пошаговая отладка команд на языке R.

![Окно среды RStudio](assets/analythics09.png)

Подробнее о работе с IDE RStudio можно узнать [тут](http://r-analytics.blogspot.ru/p/rstudio.html#.VuiE7x_fVNA)

Выполним следующий скрипт (скрипт может быть вставлен в окно Console):

```R
#подключение к dashDB
library(ibmdbR) 
mycon <- idaConnect("BLUDB", "", "") 
idaInit(mycon) 
#портирование таблиц во фреймы
temp.in <- as.data.frame(ida.data.frame('"DASH??????"."SOURCE"')[ ,c('TEMP')]) 
angle.in <- as.data.frame(ida.data.frame('"DASH??????"."SOURCE"')[ ,c('ANGLE')]) 
id.in <- as.data.frame(ida.data.frame('"DASH??????".""')[ ,c('ID')]) 
#добавление id для задания предиктивных точек
new.id <- max(id.in)+1 
id.p <- rbind(id.in,new.id)
#для искомой переменной устанавливаем значение неопределенности NA
temp.tmp <- temp.in 
new.temp <- NA 
temp.p <- rbind(temp.tmp,new.temp) 
angle.p <- rbind(angle.in,new.temp) 
#выполняем регрессионный анализ
lm1 <- predict(lm(formula = temp.p$TEMP ~ id.p$ID), temp.p) 
lm2 <- predict(lm(formula = angle.p$ANGLE ~ id.p$ID), angle.p) 
lm1.temp<-lm1[length(lm1)] 
lm2.temp<-lm2[length(lm2)] 
#выполняем вставку предиктивных данных в базу данных
query <- idaQuery("INSERT INTO ANALYTHIC (\"PREDICTTEMP\",\"PREDICTANGLE\")  VALUES (",lm1.temp,",",lm2.temp,")") 
query <- idaQuery("INSERT INTO MIXED (\"PREDICTTEMP\",\"PREDICTANGLE\")  VALUES (",lm1.temp,",",lm2.temp,")") 
```

В указанном скрипте поле DASH?????? заменить на поле User ID (имя пользователя dashDB). Нажать Enter. 
В результате скрипт будет выполнен, все использованные фреймы могут быть проанализированы на вкладке Environment.

####Запись скрипта в файловую систему окружения dashDB.

Для автоматического запуска разработанного скрипта необходимо сохранить его в рабочем пространстве проекта. Для этого необходимо перейти в косоль управления dashDB в пункт Analythics и пункт RScripts. Далее необходимо создать новый скрипт (+) и выполнить вставку кода R. Сохраним скрипт под именем predict.R .


![Запись скрипта](assets/analythics10.png)

Также можно выполнить тестовый запуск скрипта, нажав на кнопку Submit. В результате в таблицах ANLYTHICS и MIXED будут сохранены предиктивные данные.


###Запуск скрипта по расписанию из NodeRED


В редакторе NodeRed создайте следующий поток:


```json
[{"id":"5dd674c.030d48c","type":"http in","z":"7f10a56e.5876ac","name":"","url":"","method":"post","swaggerDoc":"","x":190,"y":1141,"wires":[["69516dd1.18e2a4"]]},{"id":"1d3ac371.e0f9c5","type":"http response","z":"7f10a56e.5876ac","name":"console","x":842,"y":1137,"wires":[]},{"id":"69516dd1.18e2a4","type":"function","z":"7f10a56e.5876ac","name":"","func":"msg.payload = \"cmd=RScriptRunScript&command=source(%22~/predict.R%22)&fileName=&profileName=BLUDB&userid=dash??????\";\nmsg.headers = {\"content-type\": \"application/x-www-form-urlencoded\"};\nreturn msg;","outputs":1,"noerr":0,"x":404,"y":1138,"wires":[["3831ecaa.377d34"]]},{"id":"3831ecaa.377d34","type":"http request","z":"7f10a56e.5876ac","name":"R Script","method":"POST","ret":"txt","url":"https://XXXXXXXXXXXXXXXX:8443/console/blushiftservices/BluShiftHttp.do","x":616,"y":1136,"wires":[["1d3ac371.e0f9c5","863a8702.7598a8"]]},{"id":"863a8702.7598a8","type":"debug","z":"7f10a56e.5876ac","name":"","active":true,"console":"false","complete":"false","x":959,"y":1084,"wires":[]},{"id":"e3ac94d.9075168","type":"inject","z":"7f10a56e.5876ac","name":"","topic":"","payload":"","payloadType":"date","repeat":"","crontab":"","once":false,"x":190,"y":1067.5,"wires":[["69516dd1.18e2a4"]]}]
```

В данном коде необходимо заменить следующие поля:

- dash?????? — User ID пользователя dashDB (например DASH015794)

- XXXXXXXXXXXXXX — Host name адрес dashDB приложения (например awh-yp-small03.services.dal.bluemix.net).

В блоке RScript необходимо указать значение password из настроек dashDB. Регулярность запуск задается в блоке Timestamp.


![Запуск скрипта по расписанию](assets/analythics11.png)
















