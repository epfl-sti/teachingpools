import logging

from django.core.exceptions import ObjectDoesNotExist
from ldap3 import ALL, Connection, Server

from web.models import Person, Section

logger = logging.getLogger(__name__)


def get_sciper(email):
    ldap_server = Server('ldap.epfl.ch', use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search('o=epfl,c=ch', '(&(mail={})(uniqueIdentifier=*))'.format(email),
                attributes=['uniqueIdentifier'], size_limit=1)

    assert len(conn.entries) == 1

    for entry in conn.entries:
        return str(entry['uniqueIdentifier'])


def run():
    sections = ['SEL',
                'SGM',
                'SMT',
                'SMX']

    sections_dict = dict()

    for section in sections:
        obj, obj_created = Section.objects.get_or_create(name=section)
        if obj_created:
            obj.save()
        sections_dict[section] = obj

    prof_sections = dict()
    prof_sections['abdeljalil.sayah@epfl.ch'] = 'SMT'
    prof_sections['adil.koukab@epfl.ch'] = 'SEL'
    prof_sections['adrian.ionescu@epfl.ch'] = 'SEL'
    prof_sections['aicha.hessler@epfl.ch'] = 'SMX'
    prof_sections['alain.prenleloup@epfl.ch'] = 'SGM'
    prof_sections['alain.schorderet@epfl.ch'] = 'SGM'
    prof_sections['alain.vachoux@epfl.ch'] = 'SEL'
    prof_sections['alexandre.schmid@epfl.ch'] = 'SMT'
    prof_sections['alexandre.terrier@epfl.ch'] = 'SGM'
    prof_sections['ali.sayed@epfl.ch'] = 'SEL'
    prof_sections['alireza.karimi@epfl.ch'] = 'SGM'
    prof_sections['amin.kaboli@epfl.ch'] = 'SGM'
    prof_sections['andras.kis@epfl.ch'] = 'SEL'
    prof_sections['andre.decurnex@epfl.ch'] = 'SEL'
    prof_sections['andre.hodder@epfl.ch'] = 'SMT'
    prof_sections['andreas.burg@epfl.ch'] = 'SEL'
    prof_sections['anja.skrivervik@epfl.ch'] = 'SEL'
    prof_sections['anna.fontcuberta-morral@epfl.ch'] = 'SMX'
    prof_sections['athanasios.polydoros@epfl.ch'] = 'SMT'
    prof_sections['aude.billard@epfl.ch'] = 'SGM'
    prof_sections['auke.ijspeert@epfl.ch'] = 'SGM'
    prof_sections['baptiste.busch@epfl.ch'] = 'SMT'
    prof_sections['bertrand.lacour@epfl.ch'] = 'SGM'
    prof_sections['camille.bres@epfl.ch'] = 'SEL'
    prof_sections['carlotta.guiducci@epfl.ch'] = 'SEL'
    prof_sections['catherine.dehollain@epfl.ch'] = 'SEL'
    prof_sections['cecile.hebert@epfl.ch'] = 'SMX'
    prof_sections['christian.enz@epfl.ch'] = 'SMT'
    prof_sections['christian.gaumier@epfl.ch'] = 'SEL'
    prof_sections['christian.koechli@epfl.ch'] = 'SMT'
    prof_sections['christophe.ballif@epfl.ch'] = 'SMT'
    prof_sections['christophe.moser@epfl.ch'] = 'SMT'
    prof_sections['christophe.nicolet@epfl.ch'] = 'SGM'
    prof_sections['christophe.salzmann@epfl.ch'] = 'SGM'
    prof_sections['christopher.plummer@epfl.ch'] = 'SMX'
    prof_sections['claude.nicollier@epfl.ch'] = 'SEL'
    prof_sections['claudio.bruschini@epfl.ch'] = 'SMT'
    prof_sections['colin.jones@epfl.ch'] = 'SGM'
    prof_sections['cyril.botteron@epfl.ch'] = 'SMT'
    prof_sections['cyril.cayron@epfl.ch'] = 'SMX'
    prof_sections['damien.friot@epfl.ch'] = 'SGM'
    prof_sections['danick.briand@epfl.ch'] = 'SMT'
    prof_sections['dario.floreano@epfl.ch'] = 'SGM'
    prof_sections['david.atienza@epfl.ch'] = 'SEL'
    prof_sections['demetri.psaltis@epfl.ch'] = 'SMT'
    prof_sections['denis.gillet@epfl.ch'] = 'SEL'
    prof_sections['dimitri.vandeville@epfl.ch'] = 'SMT'
    prof_sections['dimitris.kiritsis@epfl.ch'] = 'SGM'
    prof_sections['dirk.grundler@epfl.ch'] = 'SMX'
    prof_sections['dominique.pioletti@epfl.ch'] = 'SGM'
    prof_sections['dragan.damjanovic@epfl.ch'] = 'SMX'
    prof_sections['drazen.dujic@epfl.ch'] = 'SEL'
    prof_sections['duncan.alexander@epfl.ch'] = 'SMX'
    prof_sections['elison.matioli@epfl.ch'] = 'SEL'
    prof_sections['emmanuelle.boehm@epfl.ch'] = 'SMX'
    prof_sections['eric.boillat@epfl.ch'] = 'SGM'
    prof_sections['ernstrudolf.zurcher@epfl.ch'] = 'SMX'
    prof_sections['esther.amstad@epfl.ch'] = 'SMX'
    prof_sections['eva.klok@epfl.ch'] = 'SMX'
    prof_sections['fabien.sorin@epfl.ch'] = 'SMX'
    prof_sections['farhad.rachidi@epfl.ch'] = 'SEL'
    prof_sections['flavio.noca@epfl.ch'] = 'SGM'
    prof_sections['francesco.mondada@epfl.ch'] = 'SMT'
    prof_sections['francesco.stellacci@epfl.ch'] = 'SMX'
    prof_sections['francois.avellan@epfl.ch'] = 'SGM'
    prof_sections['francois.fleuret@epfl.ch'] = 'SEL'
    prof_sections['francois.gallaire@epfl.ch'] = 'SGM'
    prof_sections['francois.marechal@epfl.ch'] = 'SGM'
    prof_sections['frank.nuesch@epfl.ch'] = 'SMX'
    prof_sections['franz-josef.haug@epfl.ch'] = 'SMT'
    prof_sections['frederic.chautems@epfl.ch'] = 'SMT'
    prof_sections['giancarlo.ferraritrecate@epfl.ch'] = 'SGM'
    prof_sections['giovanni.boero@epfl.ch'] = 'SMT'
    prof_sections['giovanni.demicheli@epfl.ch'] = 'SEL'
    prof_sections['giulia.tagliabue@epfl.ch'] = 'SGM'
    prof_sections['guillermo.villanueva@epfl.ch'] = 'SGM'
    prof_sections['guy.delacretaz@epfl.ch'] = 'SMT'
    prof_sections['hans.limberger@epfl.ch'] = 'SMT'
    prof_sections['harald.vanlintel@epfl.ch'] = 'SMT'
    prof_sections['harm-anton.klok@epfl.ch'] = 'SMX'
    prof_sections['helena.vanswygenhoven@epfl.ch'] = 'SMX'
    prof_sections['herbert.shea@epfl.ch'] = 'SMT'
    prof_sections['herve.bourlard@epfl.ch'] = 'SEL'
    prof_sections['herve.lissek@epfl.ch'] = 'SEL'
    prof_sections['holger.frauenrath@epfl.ch'] = 'SMX'
    prof_sections['homeira.sunderland@epfl.ch'] = 'SMX'
    prof_sections['igor.stolitchnov@epfl.ch'] = 'SMX'
    prof_sections['ilan.vardi@epfl.ch'] = 'SMT'
    prof_sections['jamie.paik@epfl.ch'] = 'SGM'
    prof_sections['jan.vanherle@epfl.ch'] = 'SMX'
    prof_sections['jean-francois.ferrot@epfl.ch'] = 'SGM'
    prof_sections['jean-marc.vesin@epfl.ch'] = 'SEL'
    prof_sections['jean-marie.drezet@epfl.ch'] = 'SMX'
    prof_sections['jean-michel.sallese@epfl.ch'] = 'SEL'
    prof_sections['jean-philippe.thiran@epfl.ch'] = 'SEL'
    prof_sections['joel.cugnoni@epfl.ch'] = 'SGM'
    prof_sections['johann.michler@epfl.ch'] = 'SMX'
    prof_sections['john.botsis@epfl.ch'] = 'SMX'
    prof_sections['john.kolinski@epfl.ch'] = 'SGM'
    prof_sections['jose.millan@epfl.ch'] = 'SEL'
    prof_sections['juergen.brugger@epfl.ch'] = 'SMT'
    prof_sections['jurg.schiffmann@epfl.ch'] = 'SGM'
    prof_sections['kamiar.aminian@epfl.ch'] = 'SEL'
    prof_sections['karen.mulleners@epfl.ch'] = 'SGM'
    prof_sections['karen.scrivener@epfl.ch'] = 'SMX'
    prof_sections['kossi.agbeviade@epfl.ch'] = 'SGM'
    prof_sections['laetitia.philippe@epfl.ch'] = 'SMX'
    prof_sections['lea.deillon@epfl.ch'] = 'SMX'
    prof_sections['lionel.sofia@epfl.ch'] = 'SMX'
    prof_sections['luc.thevenaz@epfl.ch'] = 'SEL'
    prof_sections['ludger.weber@epfl.ch'] = 'SMX'
    prof_sections['maartje.bastings@epfl.ch'] = 'SMX'
    prof_sections['maher.kayal@epfl.ch'] = 'SMT'
    prof_sections['marc-antoine.habisreutinger@epfl.ch'] = 'SGM'
    prof_sections['marco.cantoni@epfl.ch'] = 'SMX'
    prof_sections['marco.mattavelli@epfl.ch'] = 'SEL'
    prof_sections['mario.paolone@epfl.ch'] = 'SEL'
    prof_sections['mark.sawley@epfl.ch'] = 'SGM'
    prof_sections['martin.gijs@epfl.ch'] = 'SMT'
    prof_sections['michael.unser@epfl.ch'] = 'SMT'
    prof_sections['michele.ceriotti@epfl.ch'] = 'SMX'
    prof_sections['mohamed.bouri@epfl.ch'] = 'SGM'
    prof_sections['mohamed.farhat@epfl.ch'] = 'SGM'
    prof_sections['mohammad.kahrobaiyan@epfl.ch'] = 'SMT'
    prof_sections['nicola.marzari@epfl.ch'] = 'SMX'
    prof_sections['nicolas.wyrsch@epfl.ch'] = 'SMT'
    prof_sections['niels.quack@epfl.ch'] = 'SMT'
    prof_sections['nikolaos.stergiopulos@epfl.ch'] = 'SGM'
    prof_sections['olivier.martin@epfl.ch'] = 'SMT'
    prof_sections['paolo.germano@epfl.ch'] = 'SMT'
    prof_sections['pascal.frossard@epfl.ch'] = 'SEL'
    prof_sections['patrik.hoffmann@epfl.ch'] = 'SMT'
    prof_sections['paul.bowen@epfl.ch'] = 'SMX'
    prof_sections['paul.muralt@epfl.ch'] = 'SMX'
    prof_sections['pavel.kejik@epfl.ch'] = 'SMT'
    prof_sections['pedro.reis@epfl.ch'] = 'SGM'
    prof_sections['peter.ott@epfl.ch'] = 'SGM'
    prof_sections['philip.moll@epfl.ch'] = 'SMX'
    prof_sections['philippe.muellhaupt@epfl.ch'] = 'SGM'
    prof_sections['philippe.renaud@epfl.ch'] = 'SMT'
    prof_sections['philippe.wieser@epfl.ch'] = 'SGM'
    prof_sections['pierre-andre.besse@epfl.ch'] = 'SMT'
    prof_sections['pierre-etienne.bourban@epfl.ch'] = 'SMX'
    prof_sections['pierre-yves.rochat@epfl.ch'] = 'SGM'
    prof_sections['pierre.vandergheynst@epfl.ch'] = 'SEL'
    prof_sections['rachid.cherkaoui@epfl.ch'] = 'SEL'
    prof_sections['roberto.zoia@epfl.ch'] = 'SEL'
    prof_sections['roland.loge@epfl.ch'] = 'SMX'
    prof_sections['romain.fleury@epfl.ch'] = 'SEL'
    prof_sections['sandro.carrara@epfl.ch'] = 'SEL'
    prof_sections['sebastian.gautsch@epfl.ch'] = 'SMX'
    prof_sections['sebastien.vaucher@epfl.ch'] = 'SMX'
    prof_sections['selman.sakar@epfl.ch'] = 'SGM'
    prof_sections['silvestro.micera@epfl.ch'] = 'SEL'
    prof_sections['simon.henein@epfl.ch'] = 'SMT'
    prof_sections['sophia.haussener@epfl.ch'] = 'SGM'
    prof_sections['stefano.mischler@epfl.ch'] = 'SMX'
    prof_sections['stefano.moret@epfl.ch'] = 'SGM'
    prof_sections['stephan.siegmann@epfl.ch'] = 'SMX'
    prof_sections['stephanie.lacour@epfl.ch'] = 'SMT'
    prof_sections['sylvie.roke@epfl.ch'] = 'SMT'
    prof_sections['thomas.gmuer@epfl.ch'] = 'SGM'
    prof_sections['thomas.lehnert@epfl.ch'] = 'SMT'
    prof_sections['till.junge@epfl.ch'] = 'SGM'
    prof_sections['tobias.kippenberg@epfl.ch'] = 'SMT'
    prof_sections['tobias.schneider@epfl.ch'] = 'SGM'
    prof_sections['toralf.scharf@epfl.ch'] = 'SMT'
    prof_sections['touradj.ebrahimi@epfl.ch'] = 'SEL'
    prof_sections['vasiliki.tileli@epfl.ch'] = 'SMX'
    prof_sections['veronique.michaud@epfl.ch'] = 'SMX'
    prof_sections['vivek.subramanian@epfl.ch'] = 'SMT'
    prof_sections['volkan.cevher@epfl.ch'] = 'SEL'
    prof_sections['wcraig.carter@epfl.ch'] = 'SMX'
    prof_sections['william.curtin@epfl.ch'] = 'SGM'
    prof_sections['yusuf.leblebici@epfl.ch'] = 'SEL'
    prof_sections['yves.bellouard@epfl.ch'] = 'SMT'
    prof_sections['yves.leterrier@epfl.ch'] = 'SMX'
    prof_sections['yves.perriard@epfl.ch'] = 'SMT'

    for key, value in prof_sections.items():
        try:
            sciper = get_sciper(key)
            person = Person.objects.get(sciper=sciper)
            person.section = sections_dict[value]
            person.save()
        except ObjectDoesNotExist:
            print("{} -> {} -> user not found".format(key, sciper))
            logger.error("{} -> {} -> user not found".format(key, sciper))
