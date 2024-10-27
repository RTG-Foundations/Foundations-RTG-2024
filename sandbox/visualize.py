import vpython

color_irr = vpython.color.orange
color_refl = vpython.color.white
color_edge = vpython.color.white
color_startrr = vpython.color.orange


def visualize_3d(graph, positions):
    # draw nodes:
    for node in graph:
        coord = positions[node]
        v = vpython.vector(coord[0], coord[1], coord[2])

        # refl/irrefl:
        if ((node, node) in graph.edges):
            color = color_refl
            opacity = 0.5
        else:
            color = color_irr
            opacity = 1

        vpython.points(pos=[v], color=color, opacity=opacity)

    # draw edges:
    for edge in graph.edges:
        if (edge[0] != edge[1]):
            coordinates_start = positions[edge[0]]
            coordinates_end = positions[edge[1]]

            vector_start = vpython.vector(
                coordinates_start[0],
                coordinates_start[1],
                coordinates_start[2]
            )

            vector_end = vpython.vector(
                coordinates_end[0],
                coordinates_end[1],
                coordinates_end[2]
            )

            vpython.curve(pos=[vector_start, vector_end], color=color_edge)
            vector_arrow = vector_end - vector_start
            axis = 0.5*vector_arrow
            vpython.arrow(
                pos=vector_start + 0.5*vector_arrow,
                axis=axis,
                color=color_startrr,
                shaftwidth=0.000001,
                headwidth=0.075,
                headlength=vpython.mag(vector_arrow)/3,
                round=True,
                opacity=0.5)
            # cone(pos=pos, axis=ax, color=color_startrr,   radius=0.02)

    input("Press any key to exit")
