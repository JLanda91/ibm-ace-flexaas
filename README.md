# Eindopdracht 2020

## Inleiding en motivatie
Haast alle (geautomatiseerde) unit-tests van ACE projecten betreffen slechts vergelijkingen van de input- en outputberichten van de hele flow. De "unit" in dit geval is dus een hele messageflow: erg ruim voor een unit. Echter ondergaat een bericht in transit verschillende tussenstappen, langs de nodes van een messageflow. Ook deze tussenstappen in ACE zijn te bekijken (middels de ACE Admini REST API), en in het verlengde kun je hiermee dus ook tests afnemen. Dit resulteert in fijngekorrelde unit-tests.

Deze repository bevat een set Kubernetes-native componenten en API's in Python die integreren met deze ACE Admin REST API en elkaar om zo een platform aan te bieden voor het API-matig verkrijgen van velddata op elk mogelijke tussenstap die het bericht onderging in een ACE flow. Omdat het een opzet in API's betreft, is hier in elke mogelijke taal mee te integreren in de vorm van scripting, client classes, enz. 

Key selling points:
- Gebouwd met het cutting edge technologie: Kubernetes-native en integratie met ACE 
- Staat tests toe op velddata op elk punt in de messageflow
- Opzet in API's biedt ruime integratiemogelijkheid
- Herbruikbare code en classes in Python package voor beheer en versionering.

## ACE Flow Exerciser & Test Records
De meest prominente functionaliteit waarvan in dit project extensief gebruikt wordt gemaakt is de mogelijkheid tot het API-matig integreren met wat we in de toolkit kennen als de Flow Exerciser. Je ziet na het exercisen van een bericht langs welke connecties (pijltjes) het bericht is gekomen en je kunt de vier root trees (message, LocalEnvironment, Environment en ExceptionList) bekijken.

### Flow recording en injecting
Het recorden zet je per messageflow aan, en om een bericht te kunnen exercisen kan behalve het van buiten aanroepen, ook injection aangezet worden. Uiteindelijk worden de test records opgehaald en verwijderd. Het voordeel van injection t.o.v. het van buiten inbrengen van het bericht is dat injection invariant is onder het type input node en dus het benaderprotocol (HTTP/MQ/enz).

> ```POST /apiv2/{project_type}/{project_name}/messageflows/{messageflow_name}/start-recording```

> ```POST /apiv2/{project_type}/{project_name}/messageflows/{messageflow_name}/stop-recording```

> ```POST /apiv2/{project_type}/{project_name}/messageflows/{messageflow_name}/start-injection```

> ```POST /apiv2/{project_type}/{project_name}/messageflows/{messageflow_name}/stop-injection```

> ```GET /apiv2/data/recorded-test-data```

> ```DELETE /apiv2/data/recorded-test-data```

### Test records
De test records die hieruit volgen zien er als volgt uit
```json
{
        "checkpoint": {
            "messageFlowData": {
                "integrationServer": "LOCALSERVER",
                "application": "FICO27_B2BInvoice_Demo",
                "isDefaultApplication": False,
                "library": "",
                "messageFlow": "FICO27_B2BInvoice",
                "threadId": 12300,
                "nodes": {
                    "propagationType": "terminal",
                    "source": {
                        "name": "HTTP Input",
                        "identifier": "FICO27_B2BInvoice#FCMComposite_1_1",
                        "type": "ComIbmWSInputNode",
                        "terminal": "out",
                        "inputNode": True
                    },
                    "target": {
                        "name": "RequestMapping",
                        "identifier": "FICO27_B2BInvoice#FCMComposite_1_2",
                        "type": "ComIbmComputeNode",
                        "terminal": "in"
                    }
                }
            },
            "sequenceData": {
                "serverSequenceNumber": 1,
                "flowSequenceNumber": 1,
                "threadSequenceNumber": 1,
                "connectionSequenceNumber": 1,
                "timestamp": "2020-11-22 12:40:57.508999"
            },
            "correlationData": {
                "invocationUUID": "f1f18e12-f07d-4a10-b2d1-966de4588911",
                "inputMessageUUID": "f1f18e12-f07d-4a10-b2d1-966de4588911"
            }
        },
        "testData": {
            "message": "PG1lc3NhZ...",
            "localEnvironment": "PGxvY2F...",
            "environment": "",
            "exceptionList": ""
        }
    }
```

En zoals je ziet, zit een record vol bruikbare info:
- Tussen welke twee terminals van welke nodes en in welke flow van welke applicatie en van welke server is dit record
- Sequence numbers zodat de volgorde van de connecties waarover het bericht ging bepaald kan worden
- Correlation data: invocationUUID is hetzelfde als inputMessageUUID als dit de eerste connectie was waar het bericht overheen ging.
- Base64 encoded IIB XML root trees (message, localEnvironment, Environment, exceptionList).

## Functionaliteit componenten
![Overview Componenten](doc/Components.png)

### inputmsg-collection
Een Kubernetes CronJob die je kunt configureren om naar een acceptatie-ACE te wijzen die elke keer:
1. Alle ACE records ophaalt en de input messages (invocationUUID = inputMessageUUID) laat opslaan via de inputmsg-api.
2. Haalt via de ACE Admin REST API alle draaiende projecten op en zet recording aan op al deze flows.

Beschouwbaar als een de component van een automatic message store die berichten op interval basis ophaalt.

### inputmsg-api
Een API die dient als message store. Je kunt hier handmatig records heensturen, en de API zal alleen de input messages opslaan op disk (gescheiden per integration server, project type, project naam, messageflow en input node). De inputmsg-collection component stuurt hier ook de gevonden records heen.

### stub-endpoint
Simpel API met een in-memory cache voor mock responses:
- mock id: zelf op te geven door de gebruiker.
- mock value: mock response als string.
De key is op te geven als parameter (```?id=```). Vergelijkbaar met een Redis instantie. Dit is handig als ACE backend services aan moet roepen die gemockt moeten worden. Operaties voor toevoegen/ophalen van mock responses, en het opschonen van de in-memory cache.

### unit-test-api
Een API met een Query resource en een exerciser. 
- XPath queries kunnen worden aangemaakt en opgevraagd per project type, project naam, message flow naam, node en terminal.
- De exerciser slikt een testData JSON (zoals in de test records: met base64 encoded root trees) en inject dit in gespecificeerde input node van de input node van de messageflow. Recording wordt dan ingeschakeld. De records die terug komen worden gesorteert op sequence numbers en als de van/naar node en terminal matchen met de Query resource, wordt deze XPath uitgevoerd en het resultaat bewaard. De exerciser API geeft een object terug met info over de nodes en terminals die in volgorde worden geraakt, met per connectie de geraakte queries en de resultaten.

## Kubernetes architectuur

### Exposen van apps
De meeste componenten gebruiken de volgende Kubernetes opzet:

![Overview Componenten](doc/exposing apps.png)

Dit geldt voor:
- ace-test en ace-accp (slechts één pod per test/accp deployment). Gebruikt geen PV en PVC (Persistent Volumes en Persistent Volume Claims).
- inputmsg-api.
- unit-test api.
- stub-endpoint, exclusief de PV en PVC.

Een vlugge uitleg voor de Kubernetes leken:
- De Kubernetes pods bevatten de applicatie, hebben elk hun eigen IP (wat wisselt met het omvallen en herstarten van containers), en zijn onbereikaar van buitenaf.
- Een Kubernetes service is een object dat één IP heeft en poorten naar bepaalde pod poorten doorverwijzen. Zo zijn alle pods van een deployment intern bereikbaar met adres ``` k8s_servicenaam.k8s_namespace:port```.
- Een Kubernetes ingress verbindt een subdomein en eventueel uri prefixes met een kubernetes service. Zo kun je elegant je service benaderen met ```subdomain.cloudhostname.com/uri```. Gebruik hiervan is afhankelijk van de ingress controller die je cloud met zich meeneemt. 
- Een Kubernetes PVC (PersistentVolumeClaim) wordt aan een pod gebonden en zorgt dat er ruimte gereserveerd wordt op een PV (PersistenVolume). In het geval van de (IBM) cloud wordt er cloud block/file storage aangemaakt.

> *Opmerking: de IBM Cloud ingress controller biedt geen 'SSL passthrough', wat inhoudt dat de controller inkomend verkeer niet versleuteld kan doorsturen naar backend apps. Dit heet 'SSL termination'. Daarom zijn alle apps niet met HTTPS versleuteld, wat niet nodig is omdat het inkomend verkeer op de cloud ingress service wel versleuteld is en alles binnen Kubernetes onbereikbaar is van buiten.*


## Installatie
Alle Kubernetes resources kunnen gemakkelijk geïnstalleerd worden met de Helm chart:

1. Open de Helm chart values: ```helm/ace-unit-test-util/values.yaml``` en pas aan waar nodig (zie subsectie over de uitleg van de helm chart values) 
2. Creëer de namespace voor de componenten: ```kubectl create ns <namespace>```
3. Installeer de Helm chart: ```helm install ace-unit-test-util .\helm\ace-unit-test-util\ -n <namespace>```

### Helm chart values
TBD
