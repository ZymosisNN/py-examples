from xml.etree import ElementTree as tree

sample = '''<feed  version="1.0" hasPendingRequests="false" >
  <company></company>
  <status>200</status>
  <errmsg>OK</errmsg>
  <interval>0</interval>
    <entry type="predatasource">
        <version>1638365954</version>
        <name>Push_kg_service_KG data source</name>
        <displayedas>KG data source</displayedas>
        <description></description>
        <collector>pushmodules</collector>
        <hasMultiInstances>true</hasMultiInstances>
        <schedule>60</schedule>
        <appliesTo>hasPushModules(&#34;Push_kg_service_KG data source&#34;)</appliesTo>
        <wildcardauto>false</wildcardauto>
        <wildcardpersist>false</wildcardpersist>
        <wildcardlinuxscript></wildcardlinuxscript>
        <wildcardlinuxcmdline></wildcardlinuxcmdline>
        <wildcardwinscript></wildcardwinscript>
        <wildcardwincmdline></wildcardwincmdline>
        <wildcardgroovyscript></wildcardgroovyscript>
        <wildcardschedule>1440</wildcardschedule>
        <wildcarddisable>false</wildcarddisable>
        <wildcarddeleteinactive>false</wildcarddeleteinactive>
        <agdmethod>none</agdmethod>
        <agdparams></agdparams>
        <group>kg_service_datasources</group>
        <tags></tags>
        <technology></technology>
        <adlist><![CDATA[{"agdmethod":"none","agdparams":"","id":0,"filters":[],"params":{}}]]></adlist>
        <schemaVersion>2</schemaVersion>
        <dataSourceType>1</dataSourceType>
        <attributes>
        </attributes>
        <datapoints>
        <datapoint>
            <name>point_1</name>
            <dataType>7</dataType>
            <type>2</type>
            <postprocessormethod>none</postprocessormethod>
            <postprocessorparam></postprocessorparam>
            <usevalue></usevalue>
            <alertexpr></alertexpr>
            <alertmissing>1</alertmissing>
            <alertsubject></alertsubject>
            <alertbody></alertbody>
            <enableanomalyalertsuppression></enableanomalyalertsuppression>
            <adadvsettingenabled>false</adadvsettingenabled>
            <warnadadvsetting></warnadadvsetting>
            <erroradadvsetting></erroradadvsetting>
            <criticaladadvsetting></criticaladadvsetting>
            <description></description>
            <maxvalue></maxvalue>
            <minvalue></minvalue>
            <userparam1>none</userparam1>
            <userparam2></userparam2>
            <userparam3></userparam3>
            <iscomposite>false</iscomposite>
            <rpn></rpn>
            <alertTransitionIval>5</alertTransitionIval>
            <alertClearTransitionIval>0</alertClearTransitionIval>
        </datapoint>
        <datapoint>
            <name>point_3</name>
            <dataType>7</dataType>
            <type>2</type>
            <postprocessormethod>none</postprocessormethod>
            <postprocessorparam></postprocessorparam>
            <usevalue></usevalue>
            <alertexpr>delta&#62; 11 22 33</alertexpr>
            <alertmissing>1</alertmissing>
            <alertsubject></alertsubject>
            <alertbody></alertbody>
            <enableanomalyalertsuppression></enableanomalyalertsuppression>
            <adadvsettingenabled>false</adadvsettingenabled>
            <warnadadvsetting></warnadadvsetting>
            <erroradadvsetting></erroradadvsetting>
            <criticaladadvsetting></criticaladadvsetting>
            <description></description>
            <maxvalue></maxvalue>
            <minvalue></minvalue>
            <userparam1>none</userparam1>
            <userparam2></userparam2>
            <userparam3></userparam3>
            <iscomposite>false</iscomposite>
            <rpn></rpn>
            <alertTransitionIval>5</alertTransitionIval>
            <alertClearTransitionIval>0</alertClearTransitionIval>
        </datapoint>
        <datapoint>
            <name>point_2</name>
            <dataType>7</dataType>
            <type>2</type>
            <postprocessormethod>none</postprocessormethod>
            <postprocessorparam></postprocessorparam>
            <usevalue></usevalue>
            <alertexpr>delta&#62; 30</alertexpr>
            <alertmissing>1</alertmissing>
            <alertsubject></alertsubject>
            <alertbody></alertbody>
            <enableanomalyalertsuppression></enableanomalyalertsuppression>
            <adadvsettingenabled>false</adadvsettingenabled>
            <warnadadvsetting></warnadadvsetting>
            <erroradadvsetting></erroradadvsetting>
            <criticaladadvsetting></criticaladadvsetting>
            <description></description>
            <maxvalue></maxvalue>
            <minvalue></minvalue>
            <userparam1>none</userparam1>
            <userparam2></userparam2>
            <userparam3></userparam3>
            <iscomposite>false</iscomposite>
            <rpn></rpn>
            <alertTransitionIval>5</alertTransitionIval>
            <alertClearTransitionIval>0</alertClearTransitionIval>
        </datapoint>
        </datapoints>
        <graphs>
        </graphs>
        <overviewgraphs>
        </overviewgraphs>
        <scripts>
        </scripts>
    </entry>
</feed>
'''


root = tree.fromstring(sample)

alert_expr = root.find('.//datapoint[name="point_1"]/alertexpr')

print(alert_expr)
print(alert_expr.text)
alert_expr.text = 'JOPA-JOPA'
print(tree.tostring(root))

tree.ElementTree(root).write('sample_mod.xml')
