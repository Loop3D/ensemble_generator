### scraps from egen_func.task_builder

# let's try just replacing all values at once
pt1_lines = contents[0] == '  Add3DInterfacesToFormation {'
'''this bit to find where the end of the project info and topology and included objects is and where the point info stops as well'''

pt2_lines = contents[0] == '  Add3DFoliationToFormation {'  # this bit for all interface point locations
'''this bit to find where the orientation data is defined, and also where the calc model messages are stored'''

pt3_lines = contents[0] == '    ComputeModel {'  # this bit for all interface point locations

pt1_idx = [a for a, x in enumerate(pt1_lines) if x]  # make list of row indices where the string above is found
pt2_idx = [a for a, x in enumerate(pt2_lines) if x]  # make list of row indices where the string above is found
pt3_idx = [a for a, x in enumerate(pt3_lines) if x]  # make list of row indices where the string above is found

task_pt1 = contents[0:(idx[0] - 1)]
task_pt2 = contents[(pt1_idx[0] - 1):(
            pt2_idx[0] - 1)]  # this assumes the interface points directly follow the orientation data - all the points
task_pt3 = contents[(pt2_idx[0] - 1):(
            pt3_idx[0] - 1)]  # this assumes the interface points directly follow the orientation data - all the points

'''find x, y, z for points'''
pt2_x_pattern = re.compile(r'.*(x:).*')
pt2_y_pattern = re.compile(r'.*(y:).*')
pt2_z_pattern = re.compile(r'.*(z:).*')

pt2_x_idx = np.vectorize(lambda x: bool(pt2_x_pattern.match(x)))
locs = pt2_x_idx(task_pt2[0])

pt2_x_idx = task_pt2[0].apply(lambda x: bool(pt2_x_pattern.match(x)))

pt2_x_idx = [a for a, x in enumerate(task_pt2) if x]  # make list of row indices where the string above is found
