import tkinter as tk
from PIL import Image, ImageTk
import cv2
from math import *

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.add_button()

    def add_button(self):
        # Création d'un bouton pour changer l'image
        self.button = tk.Button(self, text="distance rouge & vert", command=self.compute_distance)
        self.button.pack(side="bottom")

        # Ouverture et redimensionnement de l'image
        self.image = Image.open(image_path)
        self.image = self.image.resize((int(self.image.size[0]/2), int(self.image.size[1]/2)))
        self.photo = ImageTk.PhotoImage(self.image)

        # Affichage de l'image
        self.label = tk.Label(self, image=self.photo)
        self.label.image = self.photo
        self.label.pack(side="top")

    def compute_distance(self):
        image_ = cv2.imread(image_path)

        # Convertion de BGR à HSV (permet de mieux traiter l'image)
        hsv = cv2.cvtColor(image_, cv2.COLOR_BGR2HSV)

        # Plage de couleur pour les masques
        lower_black = (0, 0, 0)
        upper_black = (75, 75, 75)
        lower_red = (0, 50, 50)
        upper_red = (10, 255, 255)
        lower_green = (40, 50, 50)
        upper_green = (90, 255, 255)

        # Masques pour chaques couleurs
        mask_black = cv2.inRange(hsv, lower_black, upper_black)
        mask_red = cv2.inRange(hsv, lower_red, upper_red)
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        def get_points(mask, area_min):
            """
            Affiche les cercle et retourne un tableau de points
            :param mask: mask des couleurs
            :param area_min: aire minimum du point
            :return: tableau de points
            """
            point = []
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > area_min:
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)
                    cv2.circle(image_, center, radius, (0, 255, 0), 3)
                    point.append((int(x), int(y)))
            return point

        points_b = get_points(mask_black, 15)
        point_r = get_points(mask_red, 150)[0]
        point_g = get_points(mask_green, 150)[0]

        # trie des points du graphique
        points_b = sorted(points_b, key=lambda p: p[1], reverse=True)
        scale_p_x1 = sorted(points_b[2:], key=lambda p: p[0])[0]
        scale_p_x2 = sorted(points_b[2:], key=lambda p: p[0])[1]
        scale_p_y1 = sorted(points_b[:2], key=lambda p: p[0])[0]
        scale_p_y2 = sorted(points_b[:2], key=lambda p: p[0])[1]
        # calcul de l'echelle en x et en y
        scale_x_per_pixel = 30 / (scale_p_x2[0] - scale_p_x1[0])
        scale_y_per_pixel = 30 / (scale_p_y2[1] - scale_p_y1[1])

        # print(scale_p_x1, scale_p_x2, scale_p_y1, scale_p_y2)
        # print(scale_x_per_pixel, scale_y_per_pixel)

        # Calcul de la distance
        distance = sqrt(
            ((point_g[0] - point_r[0]) * scale_x_per_pixel) ** 2 + ((point_g[1] - point_r[1]) * scale_y_per_pixel) ** 2)

        # print("La distance:", distance)

        cv2.line(image_, point_r, point_g, (0, 0, 0), 4)
        text_pos = ((point_r[0] + point_g[0] - 100) // 2, (point_r[1] + point_g[1] - 100) // 2)
        cv2.putText(image_, "distance: {:.2f}".format(distance), text_pos, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2,
                    cv2.LINE_AA)

        image_ = cv2.cvtColor(image_, cv2.COLOR_BGR2RGB)
        image_ = cv2.resize(image_, (int(image_.shape[1]/2), int(image_.shape[0]/2)))

        # Conversion de l'image en ImageTk.PhotoImage
        self.photo = ImageTk.PhotoImage(Image.fromarray(image_))

        # Mise à jour de l'image affichée
        self.label.configure(image=self.photo)
        self.label.image = self.photo


image_path = "image_test_de_recrutement_EPITA_A2023.png"
root = tk.Tk()
app = App(master=root)
app.mainloop()
