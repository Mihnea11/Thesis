import matplotlib.pyplot as plt

# Date pentru diagrama procentajului de acuratețe a modelului
labels_accuracy = ['Predicții Corecte', 'Predicții Incorecte']
sizes_accuracy = [87, 13]
colors_accuracy = ['#4CAF50', '#FF5722']
explode_accuracy = (0.1, 0)  # explodează prima felie (Predicții Corecte)

# Diagrama de tip plăcintă pentru procentajul de acuratețe a modelului
fig1, ax1 = plt.subplots()
ax1.pie(sizes_accuracy, explode=explode_accuracy, labels=labels_accuracy, colors=colors_accuracy,
        autopct='%1.1f%%', shadow=True, startangle=140)
ax1.axis('equal')  # Raport de aspect egal pentru a desena diagrama sub formă de cerc.
plt.title('Procentajul de Acuratețe a Modelului')
plt.show()

# Date pentru comparația coeficientului Spearman cu PCA în diagrama de tip bară
labels_spearman = ['Random Forest', 'PCA']
values_spearman = [0.85, 0.45]
colors_spearman = ['#2196F3', '#FFC107']

# Diagrama de tip bară pentru comparația coeficientului Spearman cu PCA
fig2, ax2 = plt.subplots()
ax2.bar(labels_spearman, values_spearman, color=colors_spearman)
plt.ylabel('Coeficient Spearman')
plt.title('Comparația Coeficientului Spearman cu PCA')
plt.show()
