import re

numbers_str = """308850 - 308899	+19255	cross_fgv	 
302701 - 302708; 302750 - 302756	+19255	apco_01_fre_fgv	 
302711 - 302718; 302770 - 302775	+19255	apco_02_fre_fgv	 
303701 - 303708; 303750 - 303756	+19255	apco_03_fre_fgv	 
303711 - 303718; 303770 - 303776	+19255	apco_04_fre_fgv	 
303801 - 303808; 303850 - 303856	+19255	apco_01_fgv	 
303811 - 303818; 303870 - 303875	+19255	apco_02_fgv	 
303901 - 303908; 303950 - 303956	+19255	apco_03_fgv	 
303911 - 303918; 303970 - 303976	+19255	apco_04_fgv	 
304221 - 304228; 304261 - 304267	+19255	apco_pop_01_fre_fgv	 
304231 - 304238; 304281 - 304287	+19255	apco_pop_02_fre_fgv	 
304321 - 304328; 304361 - 304367	+19255	apco_pop_03_fre_fgv	 
304331 - 304338; 304381 - 304387	+19255	apco_pop_04_fre_fgv	 
304021 - 304028; 304061 - 304069	+19255	apco_pop_01_fgv	 
304031 - 304038; 304081 - 304087	+19255	apco_pop_02_fgv	 
304121 - 304128; 304161 - 304167	+19255	apco_pop_03_fgv	 
304131 - 304138; 304181 - 304187	+19255	apco_pop_04_fgv	 
304421 - 304428; 304461 - 304469	+19255	apco_01_light	 
304431 - 304438; 304481 - 304489	+19255	apco_01_zd	 
308800 - 308839	+19255	tsa_fgv	 
300000 - 306999	+19255	tsb_fgv	 
032101 - 032110; 002105 - 002150	+19255	tse164_fgv	 
301900 - 301949	+19255	tswebui_fgv	 
301950 - 301999	+19255	tswebui2_fgv	 
302200 - 302249	+19255	tsv_fgv	 
302500 - 302549	+19255	flow4_fgv	 
350000 - 359599	+19257	tsbb[c: 01-08]	 
000000 - 038400	3335	tsbb["",a,b,p: 01-08]	 
360000 - 362999	+19257	steady['', a, b, c, p]	 
040000 - 043600	3335	steady['', a, b, c, p]	 
100000 - 128799	3335	mgr_load["": 001-300, a,b:001-030]	 
128800 - 131199	3335	mgr_load_p	 
043700 - 053700	3335	telemrkt_mgmt ("Telemarketing Management" customer profile)	 
370000 - 373199	+19257	mgr_load_c[001-040]	 
053800 - 066800	3335	sfy (Salesify customer profile)	 
066801 - 069800	3335	place4mom (A place for mom customer profile)	 
069801 - 070000	3335	 	 
070000 - 079999	3335	PNMAC 333507xxxx	 
080000 - 099999	3335	Tempoe (cust profile)
050001 - 052000	3335	globalTel (Global Telesourcing customer profile)
310000 - 310427	+19257	xpco_ac_c	 
310500 - 310529	3335	tcpa_c2c	 
310530 - 310549	+443335	tcpa_e164_c2c	 
310550 - 310599	3335	tcpa2_c2c	 
310600 - 310629	3335	tcpa_cut_and_paste	 
310630 - 310649	+443335	tcpa_e164_cut_and_paste	 
310650 - 310699	3335	tcpa2_cut_and_paste	 
310700 - 310999	3335	lights	 
311000 - 311100	3335	pdc_tsa	 
311200 - 311400	3335	pco_light	 
311401 - 311499	3335	ws_admin2	 
320000 - 320999	3335	MM domains which names start with "mm_"	 
330000 - 344999	XXX	IVR10K domain	 
380000 - 380005	2225	Salesforce_Lightning	 
380100 - 380102	2225	amelin_tag01	 
100000 - 140000	 	big 2k domain	 
140001 - 152000	3335	sp_load	 
152001 - 152100	3335	az	 
380201 - 383000	3335	paddington_XXX(_p) domains	 
311500 - 311529	3335	tcpa2_fgv_c2c	 
311530 - 311559	3335	tcpa_fgv_cut_and_paste	 
311560 - 311589	3335	tcpa_fgv_general	 
311500 - 311529	3330	tcpa_fgv_p_c2c	 
311530 - 311559	3330	tcpa_fgv_p_cut_and_paste	 
311560 - 311589	3330	tcpa_fgv_p_general	 
311600 - 311699	+19255	webrtc_cross	 
311700 - 311799	+19255	webrtc_flow4	 
311800 - 311899	+19255	webrtc_tsa	 
311900 - 311999	+19255	webrtc_tswebui	 
312000 - 312099	+19255	webrtc_flow	 
312100 - 312199	+19255	loopback_fgv1	 
312200 - 312299	+19255	loopback_fgv2	 
312300 - 312399	+19255	flow_zd_rsp	 
312400 - 312499	+19255	flow_zd_rsp_p	 """

numbers_list = sorted([i.strip().replace(' - ', '-').replace('\t', ' ') for i in numbers_str.splitlines()])

numbers_list_final = []

for i in numbers_list:
    m1 = re.match(r'(?P<range1>\d{6}-\d{6}); +(?P<range2>\d{6}-\d{6}) +(?P<descr>.+)', i)
    m2 = re.match(r'(?P<range>\d{6}-\d{6}) +(?P<descr>.+)', i)
    if m1:
        numbers_list_final.append([m1.group('range1'), m1.group('descr')])
        numbers_list_final.append([m1.group('range2'), m1.group('descr')])
    elif m2:
        numbers_list_final.append([m2.group('range'), m2.group('descr')])
    else:
        raise Exception(i)

for i in numbers_list_final:
    print(i)
