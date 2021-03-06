import numpy as np

from ._helpers import _compose_from_faces
from ._rectangle import rectangle_quad


def disk(p, n, offset=np.pi / 2):
    k = np.arange(p)
    corners = np.vstack(
        [
            [[0.0, 0.0]],
            np.array(
                [
                    np.cos(2 * np.pi * k / p + offset),
                    np.sin(2 * np.pi * k / p + offset),
                ]
            ).T,
        ]
    )
    faces = [(0, k + 1, k + 2) for k in range(p - 1)] + [[0, p, 1]]

    def edge_adjust(edge, verts):
        if 0 in edge:
            return verts
        dist = np.sqrt(np.einsum("ij,ij->i", verts, verts))
        return verts / dist[:, None]

    def face_adjust(face, bary, verts, corner_verts):
        assert face[0] == 0
        edge_proj_bary = np.array([np.zeros(bary.shape[1]), bary[1], bary[2]]) / (
            bary[1] + bary[2]
        )
        edge_proj_cart = np.dot(corner_verts.T, edge_proj_bary).T
        dist = np.sqrt(np.einsum("ij,ij->i", edge_proj_cart, edge_proj_cart))
        return verts / dist[:, None]

    return _compose_from_faces(
        corners, faces, n, edge_adjust=edge_adjust, face_adjust=face_adjust
    )


def disk_quad(n):
    a = 1 / np.sqrt(2)
    nodes, elems = rectangle_quad((-a, -a), (a, a), n)

    # Inflate the nodes towards the circle boundary.
    # Inflate each point such that the 2-norm of the new point is the max-norm of the
    # old.
    alpha = np.max(np.abs(nodes), axis=1)
    beta = np.linalg.norm(nodes, axis=1)
    idx = beta > 1.0e-13
    nodes[idx] = (nodes[idx].T * (alpha[idx] / beta[idx])).T

    return nodes, elems
