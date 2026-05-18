from random import*
import time
import matplotlib.pyplot as plt

liste_objets=[{"val":5,"pds":2},{"val":1,"pds":3}]

"""Ex1.1"""
def validiter(objets,max,soluce):
    poids=0
    for i,valeur in enumerate(soluce):
        if valeur==True:poids+=objets[i]['pds']
    if poids<=max:return True
    return False

#print(validiter(liste_objets,5,[True,True]))

"""Ex1.2"""
def evaluation(objets,max,soluce):
    if validiter(objets,max,soluce)==False:return 0
    valeur_total=0
    for i,valeur in enumerate(soluce):
        if valeur==True:valeur_total+=objets[i]['val']
    return valeur_total

#print(evaluation(liste_objets,5,[True,False]))
"""Ex2"""
def maximum(objets,max,eval,liste_soluce):
    if len(liste_soluce)==0:return "Aucune solution proposer"
    if len(liste_soluce)==1:return liste_soluce[0]
    maximum_val=[eval(objets,max,liste_soluce[0]),0]
    for i,soluce in enumerate(liste_soluce[1:]):
        if eval(objets,max,soluce)>maximum_val[0]:maximum_val=[eval(objets,max,liste_soluce[i+1]),i+1]
    return liste_soluce[maximum_val[1]]

#print(maximum(liste_objets,4,evaluation,[[True,True],[True,False],[False,True],[False,False]]))
"""Ex3"""
def create_soluce(n):
    if n==0: return [[]]
    sous_solutions=create_soluce(n-1)
    l=[]
    for info in sous_solutions:
        l.append([False]+info)
        l.append([True]+info)
    return l    

#print(create_soluce(3))

"""Ex4"""
def bestSoluce(objets,max):
    all=create_soluce(len(objets))
    return maximum(objets,max,evaluation,all)

#print(bestSoluce(liste_objets,4))

#exponentielle

"""Ex6"""

def soluce_alea(n):
    res=[]
    for i in range(n):
        res.append(choice([True,False]))
    return res 

#print(soluce_alea(3))

"""Ex7"""
def valide_alea(objets,max):
    continu=True
    while continu:
        sol=soluce_alea(len(objets))
        map=validiter(objets,max,sol)
        if map==True:
            return sol

#print(valide_alea(liste_objets,4))

"""Ex8"""

def maximum_alea(objets,max,p):
    start=[valide_alea(objets,max),0]
    start[1]=evaluation(objets,max,start[0])
    for i in range(p-1):
        f=valide_alea(objets,max)
        if evaluation(objets,max,f)>start[1]:
            start[1]=evaluation(objets,max,f)
            start[0]=f
    return start[0]


"""Ex10"""

def tri_rapide(liste):
    if len(liste)<=1:return liste
    l1,l2=[],[]
    pivot=liste[0]
    l1=[a for a in liste[1:] if a < pivot]
    l2=[a for a in liste[1:] if a >= pivot]
    return tri_rapide(l2)+[pivot]+tri_rapide(l1)    


def glouton(objets,poids_max,evaluation):
    scores=[]
    for i in range(len(objets)):
        score=evaluation(objets[i])
        scores.append((score, i))
    scores=tri_rapide(scores)
    soluce=[False]*len(objets)
    poids_actuel=0
    for score,i in scores:
        poids_objet=objets[i]['pds']
        if poids_actuel+poids_objet<=poids_max:
            soluce[i]=True
            poids_actuel+=poids_objet
    return soluce

"""Ex11"""
def evaleur(poire):
    return poire['val']

def evalpoids(poire):
    return 1/poire['pds']
def evalatio(poire):
    return poire['val']/poire['pds']



"""Ex13"""
def ale_obj():
    return {"val":randint(1,20),"pds":randint(1,20)}

"""Ex14"""

def instance(n):
    liste=[]
    poidsTotal=0
    for i in range(n):
        new=ale_obj()
        liste.append(new)
        poidsTotal+=new['pds']
    poids_max=randint(10,max(11,poidsTotal//2))
    return liste,poids_max

"""Ex PLus"""

def solution_optimale_dp(objets, poids_max):
    n=len(objets)
    matrice = [[0 for _ in range(poids_max + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for c in range(1,poids_max + 1):
            poids_objet=objets[i-1]['pds']
            valeur_objet=objets[i-1]['val']
            if poids_objet<=c:
                matrice[i][c]=max(matrice[i-1][c],valeur_objet+matrice[i-1][c-poids_objet])
            else:
                matrice[i][c]=matrice[i-1][c]
    soluce=[False]*n
    res=matrice[n][poids_max]
    w=poids_max
    for i in range(n,0,-1):
        if res<=0:break
        if res!=matrice[i-1][w]:
            soluce[i-1]=True
            res-=objets[i-1]['val']
            w-=objets[i-1]['pds']
    return soluce

"""Ex15"""
def comparPerf():
    tailles=[2,5,8,10,12,15,18,20]
    time_brute=[]
    time_alea=[]
    time_glouton=[]
    time_dp=[]

    for n in tailles:
        print(f"Test pour n={n}")
        objets,poid_max=instance(n)

        debut=time.time()
        bestSoluce(objets,poid_max)
        time_brute.append(time.time()-debut)

        debut=time.time()
        maximum_alea(objets,poid_max,100)
        time_alea.append(time.time()-debut)

        debut=time.time()
        glouton(objets,poid_max,evalatio)
        time_glouton.append(time.time()-debut)

        debut = time.time()
        solution_optimale_dp(objets, poid_max)
        time_dp.append(time.time() - debut)

    plt.figure(figsize=(10, 6))
    plt.plot(tailles,time_brute,label="Brute force")
    plt.plot(tailles,time_alea,label="Aléatoire")
    plt.plot(tailles,time_glouton,label="Glouton")
    plt.plot(tailles, time_dp, label="DP (Optimale rapide)", color='purple', marker='D')
    plt.xlabel("Nombre d'objets")
    plt.ylabel("Temps de calcul")
    plt.legend()
    plt.grid(True)
    plt.show()




"""Ex16"""
def compEff(nb_tests=10,n_objets=15):
    ecartGloutonRatio=[]
    ecartAleaR=[]

    for i in range(nb_tests):
        objets,poid_max=instance(n_objets)
        solBrute=bestSoluce(objets,poid_max)
        valBrute=evaluation(objets,poid_max,solBrute)
        if valBrute==0:continue
        sol_glouton=glouton(objets,poid_max,evalatio)
        val_glouton=evaluation(objets,poid_max,sol_glouton)
        sol_alea=maximum_alea(objets,poid_max,100)
        val_alea=evaluation(objets,poid_max,sol_alea)

        ecartGlouton=(valBrute-val_glouton)/valBrute*100
        ecartAlea=(valBrute-val_alea)/valBrute*100
        ecartGloutonRatio.append(ecartGlouton)
        ecartAleaR.append(ecartAlea)

    moyenne_g=sum(ecartGloutonRatio)/len(ecartGloutonRatio)
    moyenne_a=sum(ecartAleaR)/len(ecartAleaR)

    print(f"Écart moyen Glouton {moyenne_g:.2f} %")
    print(f"Écart moyen Aléatoire : {moyenne_a:.2f} %")

if __name__ == "__main__":
    print(maximum_alea(liste_objets,4,10))

    print(f"Valeur : {glouton(liste_objets,15,evaleur)}")
    print(f"Poids : {glouton(liste_objets,15,evalpoids)}")
    print(f"Ratio : {glouton(liste_objets,15,evalatio)}")
    comparPerf()
    compEff()

