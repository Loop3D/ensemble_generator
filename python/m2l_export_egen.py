import networkx as nx
import random
import numpy as np
import pandas as pd
import time
import os
import pyproj

# set global vars

##########################################################################
# Save out and compile taskfile needed to generate geomodeller model using the geomodellerbatch engine
#
# loop2geomodeller(test_data_path,tmp_path,output_path,save_faults,compute_etc)
# Args:
# samples: number of models in the ensemble
# test_data_path root directory of test data
# tmp_path directory of temporary outputs
# output_path directory of outputs
# ave_faults flag for saving faults or not
# compute_etc flag for actual calculations or just project output
#
# Creates geomodeller taskfile files from varous map2loop outputs

# labels defined as generic
# 1. name (was UWA_Intrepid) - generic atm
# 2. name (was Hamersley) - generic atm
# 3. author - generic atm



# TODO check - are all the other data being input?

# TODO the args need to come from an experiement/par file - use a .py or something
'''interpolation params include:

series_calc =  which series to compute - default = all
krig_range = kriging range (float)
interface = nugget effect on interface data (float): smaller numbers = higher adherance to data, lower equals smoother
orientation = nugget effect on interface data (float): smaller numbers = higher adherance to data, lower equals smoother
drift = drift degree (int) Drift degree (0, 1 or 2): Defines the order or degree of the ‘trend’ in the data for extrapolation of the structural data.
        0 no drift, no predefined trend.
        1 linear drift, tendency to planar.
        2 quadratic drift, tendency towards parabolic
'''


##########################################################################
def l2gm_ensemble(model_path, tmp_path, output_path, dtm_file, save_faults, model_from=None, model_to=None, series_calc=None, krig_range=None, interface=None, orientation=None, drift=None):
    start_time = time.time()
    # run project parameters file
    os.chdir(model_path)  # path defined by egen_paths function
    exec(open(
        "egen_config.py").read())  # this assumes model is coming from map2loop, can make another for those comign from geomodeller (e.g. via xml parser)
    crs = pyproj.CRS.from_epsg(''.join([i for i in dst_crs['init'] if i.isdigit()]))  # m2l naming dependency = dst_crs
    bbox = (minx, miny, maxx, maxy, model_top, model_base)  # m2l naming dependency = minx, miny, maxx, maxy, model_top, model_bottom

    if not os.path.exists("./tasks"):
        os.makedirs("./tasks")
    if not os.path.exists("./ensemble"):
        os.makedirs("./ensemble")

    if model_from is None:
        model_from = 0
    if model_to is None:
        model_to = 1

    for s in range(model_from, model_to):
        loctime = time.localtime(time.time())

        f = open(model_path + '/model_' + str(s) + '.task', 'w')
        f.write('#---------------------------------------------------------------\n')
        f.write('#-----------------------Project Header-----------------------\n')
        f.write('#---------------------------------------------------------------\n')
        f.write('name: "Model_ensemble"\n')
        f.write('description: "Automate_batch_Model"\n')
        f.write('    GeomodellerTask {\n')
        f.write('    CreateProject {\n')
        f.write('        name: "model"\n')
        f.write('        author: "modeller"\n')
        f.write('        date: "' + str(loctime.tm_mday) + '/' + str(loctime.tm_mon) + '/' + str(
            loctime.tm_year) + ' ' + str(loctime.tm_hour) + ':' + str(loctime.tm_min) + ':' + str(
            loctime.tm_sec) + '"\n')
        f.write('        projection { map_projection: "' + crs.name + '"}\n')
        f.write('        version: "1.0"\n')
        f.write('        units: meters\n')
        f.write('        precision: 1.0\n')
        f.write('        Extents {\n')
        f.write('            xmin: ' + str(bbox[0]) + '\n')
        f.write('            ymin: ' + str(bbox[1]) + '\n')
        f.write('            zmin: ' + str(bbox[5]) + '\n')
        f.write('            xmax: ' + str(bbox[2]) + '\n')
        f.write('            ymax: ' + str(bbox[3]) + '\n')
        f.write('            zmax: ' + str(bbox[4]) + '\n')
        f.write('        }\n')
        f.write('        deflection2d: 0.001\n')
        f.write('        deflection3d: 0.001\n')
        f.write('        discretisation: 10.0\n')
        f.write('        referenceTop: false\n')
        f.write('        CustomDTM {\n')
        f.write('            Extents {\n')
        f.write('            xmin: ' + str(bbox[0]) + '\n')
        f.write('            ymin: ' + str(bbox[1]) + '\n')
        f.write('            xmax: ' + str(bbox[2]) + '\n')
        f.write('            ymax: ' + str(bbox[3]) + '\n')
        f.write('            }\n')
        f.write('            name: "Topography"\n')
        f.write('            filename {\n')
        f.write('                Grid_Name: "' + dtm_file + '"\n')
        f.write('            }\n')
        f.write('            nx: 10\n')
        f.write('            ny: 10\n')
        f.write('        }\n')
        f.write('    }\n')
        f.write('}\n')

        orientations = pd.read_csv(output_path + f'contacts_orient_' + str(s) + '.csv', ',')
        contacts = pd.read_csv(output_path + 'contacts_' + str(s) + '.csv', ',')
        all_sorts = pd.read_csv(tmp_path + 'all_sorts_clean.csv', ',')

        empty_fm = []

        for indx, afm in all_sorts.iterrows():
            foundcontact = False
            for indx2, acontact in contacts.iterrows():
                if (acontact['formation'] in afm['code']):
                    foundcontact = True
                    break
            foundorientation = False
            for indx3, ano in orientations.iterrows():
                if (ano['formation'] in afm['code']):
                    foundorientation = True
                    break
            if (not foundcontact or not foundorientation):
                empty_fm.append(afm['code'])

        # print(empty_fm)

        all_sorts = np.genfromtxt(tmp_path + 'all_sorts_clean.csv', delimiter=',', dtype='U100')
        nformations = len(all_sorts)

        f.write('#---------------------------------------------------------------\n')
        f.write('#-----------------------Create Formations-----------------------\n')
        f.write('#---------------------------------------------------------------\n')

        for i in range(1, nformations):
            if (not all_sorts[i, 4] in empty_fm):
                f.write('GeomodellerTask {\n')
                f.write('CreateFormation {\n')

                ostr = '    name: "' + all_sorts[i, 4].replace("\n", "") + '"\n'
                f.write(ostr)

                ostr = '    red: ' + str(random.randint(1, 256) - 1) + '\n'
                f.write(ostr)

                ostr = '    green: ' + str(random.randint(1, 256) - 1) + '\n'
                f.write(ostr)

                ostr = '    blue: ' + str(random.randint(1, 256) - 1) + '\n'
                f.write(ostr)

                f.write('    }\n')
                f.write('}\n')

        f.write('#---------------------------------------------------------------\n')
        f.write('#-----------------------Set Stratigraphic Pile------------------\n')
        f.write('#---------------------------------------------------------------\n')

        for i in range(1, nformations):
            # for i in range (nformations-1,0,-1):
            if (all_sorts[i, 2] == str(1)):
                f.write('GeomodellerTask {\n')
                f.write('SetSeries {\n')

                ostr = '    name: "' + all_sorts[i][5].replace("\n", "") + '"\n'
                f.write(ostr)

                ostr = '    position: 1\n'
                f.write(ostr)

                ostr = '    relation: "erode"\n'
                f.write(ostr)

                f.write('    }\n')
                f.write('}\n')

                for j in range(nformations - 1, 0, -1):
                    #        for j in range(1,nformations):
                    if (all_sorts[j, 1] == all_sorts[i, 1]):
                        if (not all_sorts[j][4] in empty_fm):
                            f.write('GeomodellerTask {\n')
                            f.write('AddFormationToSeries {\n')

                            ostr = '    series: "' + all_sorts[j][5] + '"\n'
                            f.write(ostr)

                            ostr = '    formation: "' + all_sorts[j][4] + '"\n'
                            f.write(ostr)

                            f.write('    }\n')
                            f.write('}\n')

        if (save_faults):
            # output_path = test_data_path + 'output/'

            faults_len = pd.read_csv(output_path + 'fault_dimensions.csv')

            n_allfaults = len(faults_len)

            fcount = 0
            for i in range(0, n_allfaults):
                f.write('GeomodellerTask {\n')
                f.write('CreateFault {\n')
                ostr = '    name: "' + faults_len.iloc[i]["Fault"] + '"\n'
                f.write(ostr)

                ostr = '    red: ' + str(random.randint(1, 256) - 1) + '\n'
                f.write(ostr)

                ostr = '    green: ' + str(random.randint(1, 256) - 1) + '\n'
                f.write(ostr)

                ostr = '    blue: ' + str(random.randint(1, 256) - 1) + '\n'
                f.write(ostr)

                f.write('    }\n')
                f.write('}\n')
                fcount = fcount + 1

                f.write('GeomodellerTask {\n')
                f.write('    Set3dFaultLimits {\n')
                f.write('        Fault_name: "' + faults_len.iloc[i]["Fault"] + '"\n')
                f.write('        Horizontal: ' + str(faults_len.iloc[i]["HorizontalRadius"]) + '\n')
                f.write('        Vertical: ' + str(faults_len.iloc[i]["VerticalRadius"]) + '\n')
                f.write('        InfluenceDistance: ' + str(faults_len.iloc[i]["InfluenceDistance"]) + '\n')
                f.write('    }\n')
                f.write('}\n')

        f.write('#---------------------------------------------------------------\n')
        f.write('#-----------------------Import 3D contact data ---Base Model----\n')
        f.write('#---------------------------------------------------------------\n')

        contacts = pd.read_csv(output_path + 'contacts_' + str(s) + '.csv', ',')
        all_sorts = pd.read_csv(tmp_path + 'all_sorts_clean.csv', ',')
        # all_sorts.set_index('code',  inplace = True)
        # display(all_sorts)

        for inx, afm in all_sorts.iterrows():
            # print(afm[0])
            if (not afm['code'] in empty_fm):
                f.write('GeomodellerTask {\n')
                f.write('    Add3DInterfacesToFormation {\n')
                f.write('          formation: "' + str(afm['code']) + '"\n')

                for indx2, acontact in contacts.iterrows():
                    if (acontact['formation'] in afm['code']):
                        ostr = '              point {x:' + str(acontact['X']) + '; y:' + str(
                            acontact['Y']) + '; z:' + str(
                            acontact['Z']) + '}\n'
                        f.write(ostr)
                f.write('    }\n')
                f.write('}\n')
        f.write('#---------------------------------------------------------------\n')
        f.write('#------------------Import 3D orientation data ---Base Model-----\n')
        f.write('#---------------------------------------------------------------\n')

        orientations = pd.read_csv(output_path + 'contacts_orient_' + str(s) + '.csv', ',')
        all_sorts = pd.read_csv(tmp_path + 'all_sorts_clean.csv', ',')
        # all_sorts.set_index('code',  inplace = True)
        # display(all_sorts)

        for inx, afm in all_sorts.iterrows():
            # print(groups[agp])
            if (not afm['code'] in empty_fm):
                f.write('GeomodellerTask {\n')
                f.write('    Add3DFoliationToFormation {\n')
                f.write('          formation: "' + str(afm['code']) + '"\n')
                for indx2, ano in orientations.iterrows():
                    if (ano['formation'] in afm['code']):
                        f.write('           foliation {\n')
                        ostr = '                  Point3D {x:' + str(ano['X']) + '; y:' + str(ano['Y']) + '; z:' + str(
                            ano['Z']) + '}\n'
                        f.write(ostr)
                        ostr = '                  direction: ' + str(ano['azimuth']) + '\n'
                        f.write(ostr)
                        ostr = '                  dip: ' + str(ano['dip']) + '\n'
                        f.write(ostr)
                        if (ano['polarity'] == 1):
                            ostr = '                  polarity: Normal_Polarity\n'
                        else:
                            ostr = '                  polarity: Reverse_Polarity\n'
                        f.write(ostr)
                        ostr = '           }\n'
                        f.write(ostr)
                f.write('    }\n')
                f.write('}\n')

        f.write('#---------------------------------------------------------------\n')
        f.write('#-----------------------Import 3D fault data ---Base Model------\n')
        f.write('#---------------------------------------------------------------\n')

        fault_contacts = pd.read_csv(output_path + 'faults_' + str(s) + '.csv', ',')
        faults = pd.read_csv(output_path + 'fault_dimensions.csv', ',')

        for indx, afault in faults.iterrows():
            f.write('GeomodellerTask {\n')
            f.write('    Add3DInterfacesToFormation {\n')
            f.write('          formation: "' + str(afault['Fault']) + '"\n')
            for indx2, acontact in fault_contacts.iterrows():
                if (acontact['formation'] == afault['Fault']):
                    ostr = '              point {x:' + str(acontact['X']) + '; y:' + str(acontact['Y']) + '; z:' + str(
                        acontact['Z']) + '}\n'
                    f.write(ostr)
            f.write('    }\n')
            f.write('}\n')

        f.write('#---------------------------------------------------------------\n')
        f.write('#------------------Import 3D fault orientation data ------------\n')
        f.write('#---------------------------------------------------------------\n')

        fault_orientations = pd.read_csv(output_path + 'faults_orient_' + str(s) + '.csv', ',')
        faults = pd.read_csv(output_path + 'fault_dimensions.csv', ',')

        for indx, afault in faults.iterrows():
            f.write('GeomodellerTask {\n')
            f.write('    Add3DFoliationToFormation {\n')
            f.write('          formation: "' + str(afault['Fault']) + '"\n')
            for indx2, ano in fault_orientations.iterrows():
                if (ano['formation'] == afault['Fault']):
                    f.write('           foliation {\n')
                    ostr = '                  Point3D {x:' + str(ano['X']) + '; y:' + str(ano['Y']) + '; z:' + str(
                        ano['Z']) + '}\n'
                    f.write(ostr)
                    ostr = '                  direction: ' + str(ano['DipDirection']) + '\n'
                    f.write(ostr)
                    if (ano['dip'] == -999):
                        ostr = '                  dip: ' + str(random.randint(60, 90)) + '\n'
                    else:
                        ostr = '                  dip: ' + str(ano['dip']) + '\n'
                    f.write(ostr)
                    if (ano['DipPolarity'] == 1):
                        ostr = '                  polarity: Normal_Polarity\n'
                    else:
                        ostr = '                  polarity: Reverse_Polarity\n'
                    f.write(ostr)
                    ostr = '           }\n'
                    f.write(ostr)
            f.write('    }\n')
            f.write('}\n')

        if (save_faults):
            G = nx.read_gml(tmp_path + "fault_network.gml", label='label')
            # nx.draw(G, with_labels=True, font_weight='bold')
            edges = list(G.edges)
            # for i in range(0,len(edges)):
            # print(edges[i][0],edges[i][1])
            cycles = list(nx.simple_cycles(G))
            # display(cycles)
            f.write('#---------------------------------------------------------------\n')
            f.write('#-----------------------Link faults with faults ----------------\n')
            f.write('#---------------------------------------------------------------\n')
            f.write('GeomodellerTask {\n')
            f.write('    LinkFaultsWithFaults {\n')

            for i in range(0, len(edges)):
                found = False
                for j in range(0, len(cycles)):
                    if (edges[i][0] == cycles[j][0] and edges[i][1] == cycles[j][1]):
                        found = True  # fault pair is first two elements in a cycle list so don't save to taskfile
                if (not found):
                    ostr = '        FaultStopsOnFaults{ fault: "' + edges[i][1] + '"; stopson: "' + edges[i][0] + '"}\n'
                    f.write(ostr)

            f.write('    }\n')
            f.write('}\n')

        if (save_faults):
            all_fault_group = np.genfromtxt(output_path + 'group-fault-relationships.csv', delimiter=',', dtype='U100')
            ngroups = len(all_fault_group)
            all_fault_group = np.transpose(all_fault_group)
            nfaults = len(all_fault_group)

            f.write('#---------------------------------------------------------------\n')
            f.write('#-----------------------Link series with faults ----------------\n')
            f.write('#---------------------------------------------------------------\n')
            f.write('GeomodellerTask {\n')
            f.write('    LinkFaultsWithSeries {\n')

            for i in range(1, nfaults):
                first = True
                for j in range(1, ngroups):
                    if (all_fault_group[i, j] == str(1)):
                        if (first):
                            ostr = '    FaultSeriesLinks{ fault: "' + all_fault_group[i, 0] + '"; series: ['
                            f.write(ostr)
                            ostr = '"' + all_fault_group[0, j] + '"'
                            f.write(ostr)
                            first = False
                        else:
                            ostr = ', "' + all_fault_group[0, j] + '"'
                            f.write(ostr)
                if (not first):
                    ostr = ']}\n'
                    f.write(ostr)

            f.write('    }\n')
            f.write('}\n')
        ####
        # Calculate model



        # assign default parameters
        if series_calc is None:
            series_c = "all"
            series_list = all_sorts.group.unique()
        else:
            series_list = series_calc
        if krig_range is None:
            krig_range = 10000.0
        if interface is None:
            interface = 0.000001
        if orientation is None:
            orientation = 0.01
        if drift is None:
            drift = 1

        calc_model_str1 = f'''\n
GeomodellerTask {{
    ComputeModel {{
        SeriesList {{'''
        f.write(calc_model_str1)

        for sc in range(len(series_list)):
            calc_model_str_series_calc = f'''
            node: "{series_list[sc]}"'''
            f.write(calc_model_str_series_calc)

        calc_model_str_section_list = f'''}}
        SectionList {{
            node: "all" }}'''
        f.write(calc_model_str_section_list)

        for ss in range(len(series_list)):
            calc_model_str2 = f'''
        SeriesInterpolationParameters {{
            series: "{series_list[ss]}"
            Range: {krig_range}
            Contacts_Nugget_Effect: {interface}
            Gradients_Nugget_Effect: {orientation}
            FaultDriftEquationDegree: {drift} }}'''
            f.write(calc_model_str2)

        calc_model_str3 = f'''
    }}
}}\n
'''
        f.write(calc_model_str3)

        ####
        f.write('GeomodellerTask {\n')
        f.write('    SaveProjectAs {\n')
        f.write('        filename: "' + model_path + '/ensemble/model_' + str(s) + '.xml"\n')
        f.write('    }\n')
        f.write('}\n')
        f.close()

    # from pyamg import solve

    # def solve_pyamg(A, B):
    #    return solve(A, B, verb=False, tol=1e-8)
    end_time = time.time()
    wall_time = (end_time - start_time)/60
    #logfile = f'This took " + str((end_time - start_time)/60) + " minutes")
    return
