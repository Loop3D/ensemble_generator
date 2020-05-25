#!/usr/bin/env python
# coding: utf-8

# ## Simple parser for geomodeller taskfile (exported as 3D contacts and orientations)

# %%
import pandas as pd
import os
import egen_func as ef

# debug - to be replaced with par file (or class??)
path_to_geomodeller = 'C:\GeoModeller\GeoModeller4.0.8_x64_88b64e610d9'
path_to_model = 'C:/Users/Mark/Cloudstor/EGen/ObjFunc_model'
xml_name = 'reallnit'

os.chdir(path_to_model)
ef.egen_paths(path_to_geomodeller, path_to_model)  # set paths
ef.egen_xml_to_task(xml_name)  # create task to convert xml to task

ef.egen_create_batch('xml_to_task.task')  # create batch file to run the xml to task conversion

os.chdir(path_to_model + '/output')
stream = os.popen('echo Returned output')
os.system('egen_batch.bat')

# taskfile_path = path+root_name+'.task'
#tasks = open('project_export.task', "r")
tasks = open('realInit.task', "r")
contents = tasks.readlines()
tasks.close()

#%% Check model directory structure

if not os.path.exists("./output"):
    os.makedirs("./output")
# if not os.path.exists("./ensemble"):
#     os.makedirs("./ensemble")


# %% Parse 3D Interface Info
os.chdir(path_to_model + '/output')
allc = open('contacts_clean.csv', "w")
allc.write('X,Y,Z,formation\n')
i = 0
for line in contents:
    if ('GeomodellerTask {' in line):
        if ('Add3DInterfacesToFormation' in contents[i + 1]):
            for j in range(i + 2, len(contents), 5):
                if ('formation' in contents[j]):
                    formation = contents[j].split(":")
                    print(formation[1].replace("\n", ""))
                    break
            for j in range(i + 2, len(contents), 5):
                if ('point' in contents[j]):
                    x = contents[j + 1].split(":")
                    y = contents[j + 2].split(":")
                    z = contents[j + 3].split(":")
                    ostr = str(x[1].replace("\n", "")) + ',' + str(y[1].replace("\n", "")) + ',' + str(
                        z[1].replace("\n", "")) + ',' + str(formation[1].replace("\n", "").replace('"', '')) + '\n'
                    allc.write(ostr)
                    # print(formation[1],x[1],y[1],z[1])
                else:
                    break
    i = i + 1
allc.close()

# %% Parse 3D Foliation Info

allo = open('orientations_clean.csv', "w")
allo.write('X,Y,Z,azimuth,dip,polarity,formation\n')
i = 0
for line in contents:
    if ('GeomodellerTask {' in line):
        if ('Add3DFoliationToFormation' in contents[i + 1]):
            formation = contents[i + 2].split(":")
            formation = formation[1].replace("\n", "")
            print(formation)

        for g in range(i + 3, len(contents), 11):
            if ('foliation' in contents[g]):

                x = contents[g + 2].split(":")
                y = contents[g + 3].split(":")
                z = contents[g + 4].split(":")
                dip = contents[g + 6].split(":")
                dipdir = contents[g + 7].split(":")
                azimuth = contents[g + 8].split(":")
                polarity = contents[g + 9].split(":")
                polarity = polarity[1].replace("\n", "").replace(" ", "")
                # if (polarity == 'Normal_Polarity'):
                #     polarity = 1
                # else:
                #     polarity = 0
                ostr = str(x[1].replace("\n", "")) + ',' + str(y[1].replace("\n", "")) + ',' + str(
                    z[1].replace("\n", "")) + ',' + str(azimuth[1].replace("\n", "")) + ',' + str(
                    dip[1].replace("\n", "")) + ',' + str(polarity) + ',' + str(formation.replace('"', '')) + '\n'
                allo.write(ostr)
                # print(x[1],y[1],z[1],azimuth[1],dip[1],polarity,formation[1])
            else:
                break
    i = i + 1
allo.close()

#%%

###################

'''the cells below relate to topology - given it is already defined in the task file, and we are net yet simulating
changes to topolgy, we don't need to parse these as they won't be input. 
Any changes to topology can (for the moment) be done with Geomodeller and saved into the project. 
'''

# %% Parse stratigraphy Info


alls = open('strat.csv', "w")
alls.write('type,series,formation,relation\n')
i = 0

for line in contents:
    if ('GeomodellerTask {' in line):
        if ('SetSeries' in contents[i + 1]):
            series = contents[i + 2].split(":")
            series = series[1].replace('"', '').replace("\n", "").replace(" ", "")
            position = contents[i + 3].split(":")
            position = position[1].replace("\n", "")
            relation = contents[i + 4].split(":")
            relation = relation[1].replace('"', '').replace("\n", "")
            print(series)
            ostr = str("0") + ',' + str(series) + ',' + str(" ") + ',' + str(relation) + '\n'
            alls.write(ostr)

            for j in range(i + 8, len(contents), 6):
                if ('AddFormationToSeries' in contents[j]):
                    formation = contents[j + 2].split(":")
                    formation = formation[1].replace("\n", "").replace('"', '').replace(" ", "")
                    ostr = str("1") + ',' + str(series) + ',' + str(formation) + ',' + str(" ") + '\n'
                    alls.write(ostr)
                    # print(x[1],y[1],z[1],azimuth[1],dip[1],polarity,formation[1])
                else:
                    break
    i = i + 1

alls.close()

# %% Parse Fault Info

allf = open('fault_info.csv', "w")
allf.write('fault_name,red,green,blue,thickness,horizontal,vertical,influedistance,type\n')
i = 0

for line in contents:
    if ('GeomodellerTask {' in line):
        if ('CreateFault' in contents[i + 1]):
            faultname = contents[i + 2].split(":")
            faultname = faultname[1].replace('"', '').replace("\n", "").replace(" ", "")
            red = contents[i + 3].split(":")
            red = red[1].replace("\n", "")
            green = contents[i + 4].split(":")
            green = green[1].replace("\n", "")
            blue = contents[i + 5].split(":")
            blue = blue[1].replace("\n", "")
            thickness = contents[i + 6].split(":")
            thickness = thickness[1].replace("\n", "")
            print(faultname, blue)

            if ('Set3dFaultLimits' in contents[i + 8]):
                horizontal = contents[i + 10].split(":")
                horizontal = horizontal[1].replace("\n", "")
                vertical = contents[i + 11].split(":")
                vertical = vertical[1].replace("\n", "")
                influedistance = contents[i + 12].split(":")
                influedistance = influedistance[1].replace("\n", "")
                if ('fault_centre' in contents[i + 14]):
                    typef = contents[i + 16].split(":")
                    typef = typef[1].replace("\n", "")
                else:
                    typef = ''
            elif ('fault_centre' in contents[i + 8]):
                typef = contents[i + 10].split(":")
                typef = typef[1].replace("\n", "")
                horizontal = 0
                vertical = 0
                influedistance = 0

            ostr = str(faultname) + ',' + str(red) + ',' + str(green) + ',' + str(blue) + ',' + str(
                thickness) + ',' + str(horizontal) + ',' + str(vertical) + ',' + str(influedistance) + ',' + str(
                typef) + '\n'
            allf.write(ostr)

    i = i + 1

allf.close()

# %% Parse Fault topology Info

allfs = open('fault_topology.csv', "w")
allfs.write('fault_name,stops_on_faults\n')
i = 0
for line in contents:
    if ('GeomodellerTask {' in line):
        if ('LinkFaultsWithFaults' in contents[i + 1]):
            inc = i + 2
            while ('FaultStopsOnFaults' in contents[inc]):
                fault = contents[inc + 1].split(":")
                fault = fault[1].replace('"', '').replace("\n", "").replace(" ", "")
                print(fault.replace("\n", ""))
                ostr = str(fault) + ','
                allfs.write(ostr)
                for k in range(inc + 2, len(contents)):
                    if ('stopson' in contents[k]):
                        faulton = contents[k].split(":")
                        faulton = faulton[1].replace('"', '').replace("\n", "")
                        ostr = str(faulton) + ';'
                        allfs.write(ostr)
                        inc = inc + 1
                    else:
                        ostr = '\n'
                        allfs.write(ostr)
                        break
                inc = inc + 3

    i = i + 1

allfs.close()

# %% Parse Fault Series topology Info

allfse = open('fault_series_topology.csv', "w")
allfse.write('fault_name,series_stops_on_faults\n')
i = 0
for line in contents:
    if ('GeomodellerTask {' in line):
        if ('LinkFaultsWithSeries' in contents[i + 1]):
            inc = i + 2
            while ('FaultSeriesLinks' in contents[inc]):
                fault = contents[inc + 1].split(":")
                fault = fault[1].replace('"', '').replace("\n", "").replace(" ", "")
                print(fault.replace("\n", ""))
                ostr = str(fault) + ','
                allfse.write(ostr)
                for k in range(inc + 2, len(contents)):
                    if ('series' in contents[k]):
                        faulton = contents[k].split(":")
                        faulton = faulton[1].replace('"', '').replace("\n", "")
                        ostr = str(faulton) + ';'
                        allfse.write(ostr)
                        inc = inc + 1
                    else:
                        ostr = '\n'
                        allfse.write(ostr)
                        break
                inc = inc + 3

    i = i + 1

allfse.close()

# %% Parse metadata

allmeta = open(xml_name + '_metadata.csv', "w")
allmeta.write('property,value\n')
i = 0
keywords = ('Grid_Name', 'map_projection', 'referenceTop', 'author', 'date')
first = True
firstname = True
for line in contents:
    if ('name' in line and firstname == True):
        firstname = False
        text = line.split(":")
        ostr = str(text[0].replace(" ", "")) + ',"' + str(
            text[2].replace("\n", "").replace(" ", "").replace("\\", "").replace('"', '')) + '"\n'
        allmeta.write(ostr)

    kw = line.split(":")
    kw = kw[0].replace(" ", "")
    if (kw in keywords):
        if ('date' in line):
            text = line.split(":")
            ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + ':' + str(
                text[2].replace("\n", "")) + ':' + str(text[3].replace("\n", "")) + '\n'
            allmeta.write(ostr)
        else:
            text = line.split(":")
            ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + '\n'
            allmeta.write(ostr)

    if ('zmax' in line and first == True):
        first = False
        text = contents[i - 5].split(":")
        ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + '\n'
        allmeta.write(ostr)
        text = contents[i - 4].split(":")
        ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + '\n'
        allmeta.write(ostr)
        text = contents[i - 3].split(":")
        ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + '\n'
        allmeta.write(ostr)
        text = contents[i - 2].split(":")
        ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + '\n'
        allmeta.write(ostr)
        text = contents[i - 1].split(":")
        ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + '\n'
        allmeta.write(ostr)
        text = contents[i].split(":")
        ostr = str(text[0].replace(" ", "")) + ',' + str(text[1].replace("\n", "")) + '\n'
        allmeta.write(ostr)
    i = i + 1

allmeta.close()

# %% Parse Petrophysics info

allp = open(xml_name + '_petrophsyics.csv', "w")
allp.write('formation,property,disttype,mean,stddev,inc,dec,percentage\n')
i = 0
for line in contents:
    if ('GeomodellerTask {' in line):
        if ('CreateFormation' in contents[i + 1]):
            inc = i + 6
            inc2 = 0
            while ('LithologyProperty' in contents[inc]):
                inc2 = 0
                k = inc + 3
                property = disttype = mean = stddev = incl = dec = percentage = 0
                if ('ProbabilityDistributionFunction' in contents[k]):  # density 1
                    formation = contents[k - 2].split(":")
                    formation = formation[1].replace('"', '').replace("\n", "").replace(" ", "")
                    prop = contents[k - 1].split(":")
                    prop = prop[1].replace('"', '').replace("\n", "").replace(" ", "")
                    print()
                    print(formation)
                    print(prop)
                    disttype = contents[k + 1].split(":")
                    disttype = disttype[1].replace('"', '').replace("\n", "")
                    mean = contents[k + 2].split(":")
                    mean = mean[1].replace('"', '').replace("\n", "")
                    stddev = contents[k + 3].split(":")
                    stddev = stddev[1].replace('"', '').replace("\n", "")
                    if (prop == 'Remanence'):
                        inc = contents[k + 4].split(":")
                        inc = inc[1].replace('"', '').replace("\n", "")
                        dec = contents[k + 5].split(":")
                        dec = dec[1].replace('"', '').replace("\n", "")
                        inc2 = 2
                    percentage = contents[k + 4 + inc2].split(":")
                    percentage = percentage[1].replace('"', '').replace("\n", "")
                    ostr = str(formation) + ',' + str(prop) + ',' + str(disttype) + ',' + str(mean) + ',' + str(
                        stddev) + ',' + str(incl) + ',' + str(dec) + ',' + str(percentage) + ',' + '\n'
                    allp.write(ostr)
                    # print(mean)

                    k = k + 10

                inc2 = 0
                if (int(percentage) < 100):  # density 2
                    k = k - 4
                    print(prop)
                    disttype = contents[k + 1].split(":")
                    disttype = disttype[1].replace('"', '').replace("\n", "")
                    mean = contents[k + 2].split(":")
                    mean = mean[1].replace('"', '').replace("\n", "")
                    stddev = contents[k + 3].split(":")
                    stddev = stddev[1].replace('"', '').replace("\n", "")
                    if (prop == 'Remanence'):
                        inc = contents[k + 4].split(":")
                        inc = inc[1].replace('"', '').replace("\n", "")
                        dec = contents[k + 5].split(":")
                        dec = dec[1].replace('"', '').replace("\n", "")
                        inc2 = 2
                    percentage = contents[k + 4 + inc2].split(":")
                    percentage = percentage[1].replace('"', '').replace("\n", "")
                    ostr = str(formation) + ',' + str(prop) + ',' + str(disttype) + ',' + str(mean) + ',' + str(
                        stddev) + ',' + str(incl) + ',' + str(dec) + ',' + str(percentage) + ',' + '\n'
                    allp.write(ostr)
                    # print(mean)

                    k = k + 10

                inc2 = 0
                if ('ProbabilityDistributionFunction' in contents[k]):  # mag sus 1
                    formation = contents[k - 2].split(":")
                    formation = formation[1].replace('"', '').replace("\n", "").replace(" ", "")
                    prop = contents[k - 1].split(":")
                    prop = prop[1].replace('"', '').replace("\n", "").replace(" ", "")
                    print(prop)

                    disttype = contents[k + 1].split(":")
                    disttype = disttype[1].replace('"', '').replace("\n", "")
                    mean = contents[k + 2].split(":")
                    mean = mean[1].replace('"', '').replace("\n", "")
                    stddev = contents[k + 3].split(":")
                    stddev = stddev[1].replace('"', '').replace("\n", "")
                    if (prop == 'Remanence'):
                        inc = contents[k + 4].split(":")
                        inc = inc[1].replace('"', '').replace("\n", "")
                        dec = contents[k + 5].split(":")
                        dec = dec[1].replace('"', '').replace("\n", "")
                        inc2 = 2
                    percentage = contents[k + 4 + inc2].split(":")
                    percentage = percentage[1].replace('"', '').replace("\n", "")
                    ostr = str(formation) + ',' + str(prop) + ',' + str(disttype) + ',' + str(mean) + ',' + str(
                        stddev) + ',' + str(incl) + ',' + str(dec) + ',' + str(percentage) + ',' + '\n'
                    allp.write(ostr)
                    # print(mean)

                    k = k + 10

                inc2 = 0
                if (int(percentage) < 100):  # mag sus 2
                    k = k - 4
                    print(prop)
                    disttype = contents[k + 1].split(":")
                    disttype = disttype[1].replace('"', '').replace("\n", "")
                    mean = contents[k + 2].split(":")
                    mean = mean[1].replace('"', '').replace("\n", "")
                    stddev = contents[k + 3].split(":")
                    stddev = stddev[1].replace('"', '').replace("\n", "")
                    if (prop == 'Remanence'):
                        inc = contents[k + 4].split(":")
                        inc = inc[1].replace('"', '').replace("\n", "")
                        dec = contents[k + 5].split(":")
                        dec = dec[1].replace('"', '').replace("\n", "")
                        inc2 = 2
                    percentage = contents[k + 4 + inc2].split(":")
                    percentage = percentage[1].replace('"', '').replace("\n", "")
                    ostr = str(formation) + ',' + str(prop) + ',' + str(disttype) + ',' + str(mean) + ',' + str(
                        stddev) + ',' + str(incl) + ',' + str(dec) + ',' + str(percentage) + ',' + '\n'
                    allp.write(ostr)
                    # print(mean)

                    k = k + 10

                inc2 = 0
                if ('ProbabilityDistributionFunction' in contents[k]):  # remanence
                    formation = contents[k - 2].split(":")
                    formation = formation[1].replace('"', '').replace("\n", "").replace(" ", "")
                    prop = contents[k - 1].split(":")
                    prop = prop[1].replace('"', '').replace("\n", "").replace(" ", "")
                    print(prop)

                    disttype = contents[k + 1].split(":")
                    disttype = disttype[1].replace('"', '').replace("\n", "")
                    mean = contents[k + 2].split(":")
                    mean = mean[1].replace('"', '').replace("\n", "")
                    stddev = contents[k + 3].split(":")
                    stddev = stddev[1].replace('"', '').replace("\n", "")
                    if (prop == 'Remanence'):
                        incl = contents[k + 4].split(":")
                        incl = incl[1].replace('"', '').replace("\n", "")
                        dec = contents[k + 5].split(":")
                        dec = dec[1].replace('"', '').replace("\n", "")
                        inc2 = 2
                    percentage = contents[k + 4 + inc2].split(":")
                    percentage = percentage[1].replace('"', '').replace("\n", "")
                    ostr = str(formation) + ',' + str(prop) + ',' + str(disttype) + ',' + str(mean) + ',' + str(
                        stddev) + ',' + str(incl) + ',' + str(dec) + ',' + str(percentage) + ',' + '\n'
                    allp.write(ostr)
                    # print(mean)

                    k = k + 10

                inc = inc + 1

    i = i + 1

allp.close()
