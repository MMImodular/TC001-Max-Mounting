import adsk.core, adsk.fusion

# Frame: lens face toward +Z (front face at Z=0), USB plug pointing +Y (top face at Y=0),
# lens end toward -X, X=0 at middle of body length. Fusion Y-up.

PARAMS = [
    # name, expression, comment
    ('body_L', '71 mm', 'Body length X. Listing 7.1 cm / 2.8 in. CONFIRMED-ish'),
    ('body_H', '31.2 mm', 'Body height, plug face to opposite face, plug excluded. ESTIMATE photo-scaled; listing says 42 incl plug? MEASURE FIRST'),
    ('body_T', '14 mm', 'Body thickness Z, lens face to back face. Listing 0.55 in. MEASURE'),
    ('endcap_W', '2 mm', 'Black end cap thickness along X. ESTIMATE'),
    ('chamfer_top', '6 mm', 'Front-view chamfer at the two plug-side corners. ESTIMATE'),
    ('chamfer_bot', '2.5 mm', 'Front-view chamfer at the two bottom corners. ESTIMATE'),
    ('bevel_front', '5.6 mm', 'Front-top long-edge bevel: height on front face. ESTIMATE'),
    ('bevel_top', '3 mm', 'Front-top long-edge bevel: depth into top face. ESTIMATE weak'),
    ('edge_R', '1 mm', 'Round on the two bottom long edges. ESTIMATE'),
    ('win_top', '6 mm', 'Lens window top edge below top face. ESTIMATE'),
    ('win_H', '23.6 mm', 'Lens window height. ESTIMATE'),
    ('win_W', '20 mm', 'Lens window width along X. ESTIMATE'),
    ('win_X0', '5.3 mm', 'Lens window bottom-left corner from -X end. ESTIMATE'),
    ('win_shear', '9.85 mm', 'Lens window slant: top edge shifted toward +X. ESTIMATE'),
    ('win_depth', '0.3 mm', 'Lens window recess depth. ESTIMATE'),
    ('vis_X', '19.9 mm', 'Upper (visible?) lens centre from -X end. ESTIMATE'),
    ('vis_Y', '12.3 mm', 'Upper (visible?) lens centre below top face. ESTIMATE'),
    ('vis_D', '9.9 mm', 'Upper lens ring diameter. ESTIMATE'),
    ('ir_X', '19.7 mm', 'Lower (thermal?) lens centre from -X end. ESTIMATE'),
    ('ir_Y', '24.1 mm', 'Lower (thermal?) lens centre below top face. ESTIMATE'),
    ('ir_D', '10.6 mm', 'Lower lens ring diameter. ESTIMATE'),
    ('lens_recess', '1 mm', 'Lens ring recess below window. ESTIMATE'),
    ('pin_D', '0.8 mm', 'Pinhole on +X end cap, diameter. ESTIMATE'),
    ('pin_Y', 'body_H / 2', 'Pinhole centre below top face. ESTIMATE'),
    ('pin_Z', '4 mm', 'Pinhole centre behind front face. ESTIMATE'),
    ('plug_X', '0 mm', 'USB-C plug centre offset along X from body centre (+ = away from lenses). ESTIMATE'),
    ('plug_Z', 'body_T / 2', 'USB-C plug centre distance behind front (lens) face. ESTIMATE weak'),
    ('usbc_W', '8.25 mm', 'USB-C plug shell width. USB Type-C spec'),
    ('usbc_T', '2.4 mm', 'USB-C plug shell thickness. USB Type-C spec'),
    ('usbc_R', '1.15 mm', 'USB-C plug shell end radius (just under usbc_T/2)'),
    ('usbc_L', '7.7 mm', 'USB-C plug exposed length, collar face to tip. ESTIMATE; spec min mating 6.65'),
    ('collar_W', '10.4 mm', 'Black collar under plug, X width. ESTIMATE'),
    ('collar_D', '4 mm', 'Black collar under plug, Z depth. ESTIMATE guess'),
    ('collar_H', '1 mm', 'Black collar height above top face (= receptacle seat). ESTIMATE'),
    ('env_clr', '0.5 mm', 'Clearance added around collar+plug for PlugEnvelope keep-out'),
    ('sk_ref', '100 mm', 'Sketch datum offset used by dimension expressions. Do not edit'),
]

CM = 0.1  # mm -> cm


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    um = design.unitsManager
    up = design.userParameters
    for name, expr, comment in PARAMS:
        p = up.itemByName(name)
        if p:
            p.expression = expr
            p.comment = comment
        else:
            up.add(name, adsk.core.ValueInput.createByString(expr), 'mm', comment)

    root = design.rootComponent
    comp = root  # Part Design documents allow a single component
    tl = design.timeline
    while tl.count > 0:
        tl.item(tl.count - 1).entity.deleteMe()

    def ev(expr):
        return um.evaluateExpression(expr, 'mm')  # cm

    def V(s):
        return adsk.core.ValueInput.createByString(s)

    feats = comp.features

    # ---------- parametric sketch helper ----------
    def new_sketch(plane, name):
        sk = comp.sketches.add(plane)
        sk.name = name
        xd, yd, o = sk.xDirection, sk.yDirection, sk.origin
        R = sk.sketchPoints.add(adsk.core.Point3D.create(-100 * CM, 100 * CM, 0))
        R.isFixed = True
        return sk, (xd, yd, o), R

    def axis_expr(direction, origin, exprs):
        # sketch coordinate = (P - O) . dir, dir is +-unit model axis
        comps = [direction.x, direction.y, direction.z]
        ocomps = [origin.x, origin.y, origin.z]
        terms, const = [], 0.0
        for i in range(3):
            if abs(comps[i]) > 0.5:
                sgn = '+' if comps[i] > 0 else '-'
                terms.append(f"{sgn}({exprs[i]})")
                const -= comps[i] * ocomps[i]
        s = ' '.join(terms)
        if abs(const) > 1e-9:
            s += f" + ({const * 10:.6f} mm)"
        return s

    def sk_point(sk, frame, model_exprs):
        xd, yd, o = frame
        vals = [ev(e) for e in model_exprs]
        p = adsk.core.Point3D.create(*vals)
        sp = sk.modelToSketchSpace(p)
        sx_e = axis_expr(xd, o, model_exprs)
        sy_e = axis_expr(yd, o, model_exprs)
        return adsk.core.Point3D.create(sp.x, sp.y, 0), sx_e, sy_e

    def pin(sk, R, spt, sx_e, sy_e, do_x=True, do_y=True):
        dims = sk.sketchDimensions
        H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
        Vv = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
        g = spt.geometry
        if do_x:
            d = dims.addDistanceDimension(R, spt, H, adsk.core.Point3D.create((g.x - 10) / 2, g.y + 1, 0))
            d.parameter.expression = f"sk_ref + ({sx_e})"
        if do_y:
            d = dims.addDistanceDimension(R, spt, Vv, adsk.core.Point3D.create(g.x + 1, (g.y + 10) / 2, 0))
            d.parameter.expression = f"sk_ref - ({sy_e})"

    def polygon(sk, frame, R, model_pts):
        pts = [sk_point(sk, frame, mp) for mp in model_pts]
        lines = sk.sketchCurves.sketchLines
        first = lines.addByTwoPoints(pts[0][0], pts[1][0])
        prev = first
        for k in range(2, len(pts)):
            prev = lines.addByTwoPoints(prev.endSketchPoint, pts[k][0])
        lines.addByTwoPoints(prev.endSketchPoint, first.startSketchPoint)
        # the API auto-adds horizontal/vertical constraints; every vertex is pinned by dimensions instead
        gc = sk.geometricConstraints
        for i in range(gc.count - 1, -1, -1):
            gc.item(i).deleteMe()
        allL = [lines.item(i) for i in range(lines.count)]
        spts = [allL[0].startSketchPoint] + [l.endSketchPoint for l in allL[:-1]]
        n = len(spts)
        # explicit H/V constraints on axis-aligned edges; one dimension per shared coordinate
        xg, yg = list(range(n)), list(range(n))

        def find(g, i):
            while g[i] != i:
                i = g[i]
            return i
        for k, ln in enumerate(allL):
            i, j = k, (k + 1) % n
            a, b = pts[i][0], pts[j][0]
            if abs(a.y - b.y) < 1e-9:
                gc.addHorizontal(ln)
                yg[find(yg, j)] = find(yg, i)
            elif abs(a.x - b.x) < 1e-9:
                gc.addVertical(ln)
                xg[find(xg, j)] = find(xg, i)
        for k, (spt, (_, sx_e, sy_e)) in enumerate(zip(spts, pts)):
            pin(sk, R, spt, sx_e, sy_e, do_x=find(xg, k) == k, do_y=find(yg, k) == k)

    def circle(sk, frame, R, center_exprs, dia_expr):
        c, sx_e, sy_e = sk_point(sk, frame, center_exprs)
        circ = sk.sketchCurves.sketchCircles.addByCenterRadius(c, ev(dia_expr) / 2)
        pin(sk, R, circ.centerSketchPoint, sx_e, sy_e)
        d = sk.sketchDimensions.addDiameterDimension(circ, adsk.core.Point3D.create(c.x + 1, c.y + 1, 0))
        d.parameter.expression = dia_expr
        return circ

    def direction_for(sk, want):  # want: model Vector3D
        n = sk.xDirection.crossProduct(sk.yDirection)
        return (adsk.fusion.ExtentDirections.PositiveExtentDirection if n.dotProduct(want) > 0
                else adsk.fusion.ExtentDirections.NegativeExtentDirection)

    def extrude(sk, profiles, dist_expr, want_dir, op, name, bodies=None):
        coll = adsk.core.ObjectCollection.create()
        for p in profiles:
            coll.add(p)
        inp = feats.extrudeFeatures.createInput(coll, op)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(dist_expr)), direction_for(sk, want_dir))
        if bodies:
            inp.participantBodies = bodies
        f = feats.extrudeFeatures.add(inp)
        f.name = name
        return f

    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    vX = adsk.core.Vector3D.create(1, 0, 0)
    vY = adsk.core.Vector3D.create(0, 1, 0)
    vZ = adsk.core.Vector3D.create(0, 0, 1)
    mX = adsk.core.Vector3D.create(-1, 0, 0)
    mZ = adsk.core.Vector3D.create(0, 0, -1)

    def offset_plane(base, expr, name, axis, sign_expected):
        pi = comp.constructionPlanes.createInput()
        pi.setByOffset(base, V(expr))
        pl = comp.constructionPlanes.add(pi)
        pl.name = name
        val = ev(expr)
        g = pl.geometry.origin
        actual = [g.x, g.y, g.z][axis]
        if abs(val) > 1e-6 and abs(actual - sign_expected * val) > 1e-4:
            pl.deleteMe()
            pi = comp.constructionPlanes.createInput()
            pi.setByOffset(base, V(f"-({expr})"))
            pl = comp.constructionPlanes.add(pi)
            pl.name = name
        return pl

    XY, XZ, YZ = comp.xYConstructionPlane, comp.xZConstructionPlane, comp.yZConstructionPlane

    # ---------- 1. body from front silhouette ----------
    sk, fr, R = new_sketch(XY, 'S_FrontSilhouette')
    polygon(sk, fr, R, [
        ('-body_L/2 + chamfer_top', '0 mm', '0 mm'),
        ('body_L/2 - chamfer_top', '0 mm', '0 mm'),
        ('body_L/2', '-chamfer_top', '0 mm'),
        ('body_L/2', '-body_H + chamfer_bot', '0 mm'),
        ('body_L/2 - chamfer_bot', '-body_H', '0 mm'),
        ('-body_L/2 + chamfer_bot', '-body_H', '0 mm'),
        ('-body_L/2', '-body_H + chamfer_bot', '0 mm'),
        ('-body_L/2', '-chamfer_top', '0 mm'),
    ])
    print('front sketch fully constrained:', sk.isFullyConstrained, 'profiles', sk.profiles.count)
    ex = extrude(sk, [sk.profiles.item(0)], 'body_T', mZ, NEW, 'Body')
    body = ex.bodies.item(0)
    body.name = 'Shell'

    tol = 1e-4
    H = ev('body_H')
    T = ev('body_T')

    # ---------- 2. front-top bevel (two-distance chamfer) ----------
    def top_front_edge():
        c = adsk.core.ObjectCollection.create()
        for e in body.edges:
            a, b = e.startVertex.geometry, e.endVertex.geometry
            if abs(a.y) < tol and abs(b.y) < tol and abs(a.z) < tol and abs(b.z) < tol:
                c.add(e)
        return c

    def make_bevel(d1, d2):
        ci = feats.chamferFeatures.createInput2()
        ci.chamferEdgeSets.addTwoDistancesChamferEdgeSet(top_front_edge(), V(d1), V(d2), False, False)
        f = feats.chamferFeatures.add(ci)
        f.name = 'FrontTopBevel'
        return f

    bev = make_bevel('bevel_front', 'bevel_top')
    bf = ev('bevel_front')
    ok = any(abs(v.geometry.z) < tol and abs(v.geometry.y + bf) < tol for v in body.vertices)
    if not ok:
        bev.deleteMe()
        bev = make_bevel('bevel_top', 'bevel_front')
        ok = any(abs(v.geometry.z) < tol and abs(v.geometry.y + bf) < tol for v in body.vertices)
    print('bevel on front face at y=-bevel_front:', ok)

    # ---------- 3. bottom long-edge rounds ----------
    c = adsk.core.ObjectCollection.create()
    for e in body.edges:
        a, b = e.startVertex.geometry, e.endVertex.geometry
        if abs(a.y + H) < tol and abs(b.y + H) < tol and abs(a.z - b.z) < tol and (abs(a.z) < tol or abs(a.z + T) < tol):
            c.add(e)
    fi = feats.filletFeatures.createInput()
    try:
        fi.edgeSetInputs.addConstantRadiusEdgeSet(c, V('edge_R'), False)
    except AttributeError:
        fi.addConstantRadiusEdgeSet(c, V('edge_R'), False)
    ff = feats.filletFeatures.add(fi)
    ff.name = 'BottomEdgeRounds'
    print('bottom round edges:', c.count)

    # ---------- 4. lens window recess ----------
    sk, fr, R = new_sketch(XY, 'S_LensWindow')
    xl = '-body_L/2 + win_X0'
    polygon(sk, fr, R, [
        (xl, '-(win_top + win_H)', '0 mm'),
        (f'{xl} + win_W', '-(win_top + win_H)', '0 mm'),
        (f'{xl} + win_W + win_shear', '-win_top', '0 mm'),
        (f'{xl} + win_shear', '-win_top', '0 mm'),
    ])
    print('window sketch fully constrained:', sk.isFullyConstrained)
    extrude(sk, [sk.profiles.item(0)], 'win_depth', mZ, CUT, 'LensWindowRecess', [body])

    # ---------- 5. lens rings ----------
    sk, fr, R = new_sketch(XY, 'S_Lenses')
    circle(sk, fr, R, ('-body_L/2 + vis_X', '-vis_Y', '0 mm'), 'vis_D')
    circle(sk, fr, R, ('-body_L/2 + ir_X', '-ir_Y', '0 mm'), 'ir_D')
    print('lens sketch fully constrained:', sk.isFullyConstrained, 'profiles', sk.profiles.count)
    profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
    extrude(sk, profs, 'win_depth + lens_recess', mZ, CUT, 'LensRings', [body])

    # ---------- 6. pinhole on +X end cap ----------
    plE = offset_plane(YZ, 'body_L/2', 'END_plusX', 0, 1)
    sk, fr, R = new_sketch(plE, 'S_Pinhole')
    circle(sk, fr, R, ('body_L/2', '-pin_Y', '-pin_Z'), 'pin_D')
    extrude(sk, [sk.profiles.item(0)], '1 mm', mX, CUT, 'Pinhole', [body])

    # ---------- 7. split end caps ----------
    pA = offset_plane(YZ, 'body_L/2 - endcap_W', 'SPLIT_capPlusX', 0, 1)
    pB = offset_plane(YZ, '-(body_L/2 - endcap_W)', 'SPLIT_capMinusX', 0, 1)
    for pl, nm in ((pA, 'SplitCapPlusX'), (pB, 'SplitCapMinusX')):
        bc = adsk.core.ObjectCollection.create()
        for b in comp.bRepBodies:
            bc.add(b)
        si = feats.splitBodyFeatures.createInput(bc, pl, True)
        sf = feats.splitBodyFeatures.add(si)
        sf.name = nm
    for b in comp.bRepBodies:
        bb = b.boundingBox
        if bb.maxPoint.x - bb.minPoint.x > 2 * ev('endcap_W') + 0.1:
            b.name = 'Shell'
        elif bb.minPoint.x > 0:
            b.name = 'EndCap_PlusX'
        else:
            b.name = 'EndCap_MinusX'

    # ---------- 8. USB-C collar, plug, envelope ----------
    sk, fr, R = new_sketch(XZ, 'S_USB_Collar')
    polygon(sk, fr, R, [
        ('plug_X - collar_W/2', '0 mm', '-plug_Z - collar_D/2'),
        ('plug_X + collar_W/2', '0 mm', '-plug_Z - collar_D/2'),
        ('plug_X + collar_W/2', '0 mm', '-plug_Z + collar_D/2'),
        ('plug_X - collar_W/2', '0 mm', '-plug_Z + collar_D/2'),
    ])
    print('collar sketch fully constrained:', sk.isFullyConstrained)
    f = extrude(sk, [sk.profiles.item(0)], 'collar_H', vY, NEW, 'USB_Collar')
    f.bodies.item(0).name = 'USB_Collar'

    plSeat = offset_plane(XZ, 'collar_H', 'PLUG_seat', 1, 1)
    sk, fr, R = new_sketch(plSeat, 'S_USB_Plug')
    polygon(sk, fr, R, [
        ('plug_X - usbc_W/2', 'collar_H', '-plug_Z - usbc_T/2'),
        ('plug_X + usbc_W/2', 'collar_H', '-plug_Z - usbc_T/2'),
        ('plug_X + usbc_W/2', 'collar_H', '-plug_Z + usbc_T/2'),
        ('plug_X - usbc_W/2', 'collar_H', '-plug_Z + usbc_T/2'),
    ])
    print('plug sketch fully constrained:', sk.isFullyConstrained)
    f = extrude(sk, [sk.profiles.item(0)], 'usbc_L', vY, NEW, 'USB_C_Plug')
    plug = f.bodies.item(0)
    plug.name = 'USB_C_Plug'
    c = adsk.core.ObjectCollection.create()
    for e in plug.edges:
        a, b = e.startVertex.geometry, e.endVertex.geometry
        if abs(a.x - b.x) < tol and abs(a.z - b.z) < tol:
            c.add(e)
    fi = feats.filletFeatures.createInput()
    try:
        fi.edgeSetInputs.addConstantRadiusEdgeSet(c, V('usbc_R'), False)
    except AttributeError:
        fi.addConstantRadiusEdgeSet(c, V('usbc_R'), False)
    ff = feats.filletFeatures.add(fi)
    ff.name = 'USB_C_PlugEnds'
    print('plug end edges:', c.count)

    sk, fr, R = new_sketch(XZ, 'S_PlugEnvelope')
    polygon(sk, fr, R, [
        ('plug_X - collar_W/2 - env_clr', '0 mm', '-plug_Z - collar_D/2 - env_clr'),
        ('plug_X + collar_W/2 + env_clr', '0 mm', '-plug_Z - collar_D/2 - env_clr'),
        ('plug_X + collar_W/2 + env_clr', '0 mm', '-plug_Z + collar_D/2 + env_clr'),
        ('plug_X - collar_W/2 - env_clr', '0 mm', '-plug_Z + collar_D/2 + env_clr'),
    ])
    f = extrude(sk, [sk.profiles.item(0)], 'collar_H + usbc_L + env_clr', vY, NEW, 'PlugEnvelope')
    env = f.bodies.item(0)
    env.name = 'PlugEnvelope'
    env.opacity = 0.25

    # ---------- 9. datum planes / axis ----------
    offset_plane(XY, '0 mm', 'FRONT_lensFace', 2, 1)
    offset_plane(XY, '-body_T', 'MOUNT_back', 2, 1)
    offset_plane(XZ, '-body_H', 'MOUNT_bottom', 1, 1)
    offset_plane(XZ, '0 mm', 'MOUNT_top', 1, 1)
    offset_plane(XZ, 'collar_H + usbc_L', 'PLUG_tip', 1, 1)
    pX = offset_plane(YZ, 'plug_X', 'PLUG_midX', 0, 1)
    pZ = offset_plane(XY, '-plug_Z', 'PLUG_midZ', 2, 1)
    ai = comp.constructionAxes.createInput()
    ai.setByTwoPlanes(pX, pZ)
    ax = comp.constructionAxes.add(ai)
    ax.name = 'PLUG_axis'
    for nm in ('PLUG_midX', 'PLUG_midZ'):
        comp.constructionPlanes.itemByName(nm).isLightBulbOn = False

    # hide sketches
    for s in comp.sketches:
        s.isVisible = False

    for b in comp.bRepBodies:
        bb = b.boundingBox
        print(b.name, 'bbox mm', [round(v * 10, 2) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z, bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)], 'vol cm3', round(b.volume, 3))
    for i in range(design.timeline.count):
        it = design.timeline.item(i)
        if it.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            print('UNHEALTHY', it.name, it.errorOrWarningMessage)
    print('timeline', design.timeline.count)
