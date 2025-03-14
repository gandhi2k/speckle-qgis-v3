import math
from typing import List

import earcut.earcut
from specklepy.objects.geometry.mesh import Mesh
from specklepy.objects.geometry.polyline import Polyline


def generate_region_mesh(boundary: Polyline, inner_loops: List[Polyline], units: str):

    max_points = 5000
    coef = math.ceil(len(boundary.value) / max_points)

    boundary_points_count = int(len(boundary.value) / 3)
    vertices3d_tuples: List[List[float]] = [
        [
            boundary.value[i * coef * 3],
            boundary.value[i * coef * 3 + 1],
            boundary.value[i * coef * 3 + 2],
        ]
        for i, _ in enumerate(boundary.value)
        if i * coef < boundary_points_count
    ]

    # inner loops
    loops3d_tuples: List[List[List[float]]] = []
    for loop in inner_loops:
        loop_points_count = int(len(loop.value) / 3)
        coef_loop = math.ceil(len(boundary.value) / max_points)

        vertices3d_loop_tuples = [
            [
                loop.value[i * coef_loop * 3],
                loop.value[i * coef_loop * 3 + 1],
                loop.value[i * coef_loop * 3 + 2],
            ]
            for i, _ in enumerate(loop.value)
            if i * coef_loop < loop_points_count
        ]

        loops3d_tuples.append(vertices3d_loop_tuples)

    # triangulate region
    triangles: List[List[int]] = _get_triangles(vertices3d_tuples, loops3d_tuples)

    # if triangulated:
    total_vertices = 0
    vertices = []
    faces = []

    for trg in triangles:
        # TODO: make sure all faces are clockwise (facing down)

        vertices.extend(
            vertices3d_tuples[trg[0]]
            + vertices3d_tuples[trg[1]]
            + vertices3d_tuples[trg[2]]
        )

        faces.extend(
            [
                3,
                total_vertices + 1,
                total_vertices + 2,
                total_vertices + 3,
            ]
        )
        total_vertices += 3

    return Mesh(vertices=vertices, faces=faces, units=units)


def _get_triangles(vertices3d_tuples, loops3d_tuples):

    # iterate through each loop (list of coordinate tuples)
    loop_indices = []
    for loop_tuple_list in loops3d_tuples:

        # current count of vertices will be the start index of the new loop
        current_count = len(vertices3d_tuples)
        loop_indices.append(current_count)
        vertices3d_tuples.extend(loop_tuple_list)

    if len(loop_indices) == 0:
        loop_indices = None

    vertices_flat_coords = [item for sub_list in vertices3d_tuples for item in sub_list]

    triangles_flat_list = earcut.earcut.earcut(
        vertices_flat_coords, loop_indices, dim=3
    )
    triangle_tuples = [
        [
            triangles_flat_list[3 * i],
            triangles_flat_list[3 * i + 1],
            triangles_flat_list[3 * i + 2],
        ]
        for i, _ in enumerate(triangles_flat_list)
        if i < len(triangles_flat_list) / 3
    ]

    return triangle_tuples
