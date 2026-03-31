ENDPOINT PÚBLICOS (Open)
GET - /charadas - (TODAS AS CHARADAS)
GET - /charadas/aleatoria - (1 charada sorteada)
GET - /charadas/id - (1 charada por id)

ENDPOINTS PRIVADOS (Autencicação bearer)
POST - /charadas - (CRIAR CHARADA)
PATCH - /charadas/<int:id> - (Alterar parcialmente pelo id)
PUT - /charadas/<int:id> - (Alterar completamente pelo id)
DELETE - /charadas/<int:id> - (Deletar charada pelo id)

Database: Firebase Firestore da google (NO SQL - NÃO RELACIONAL)
HOST: VERCEL
testando