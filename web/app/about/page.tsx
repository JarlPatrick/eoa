import type { Metadata } from "next";

export const metadata: Metadata = { title: "Meist" };

export default function AboutPage() {
  return (
    <>
      <section className="page-intro">
        <h1>Meist</h1>
        <p>
          Eesti Olümpiaadide Andmebaas koondab Eesti aineolümpiaadide tulemusi
          ühte kohta. Siit saab sirvida tulemusi õppeaine, olümpiaadi ja
          õppeaasta järgi ning uurida osalejate ja koolide seoseid.
        </p>
        <p>
          Andmebaas on mitteametlik ega ole seotud ühegi olümpiaade korraldava
          organisatsiooniga.
        </p>
        <p>
          Andmebaasi eesmärk on säilitada varasemad tulemused ja teha need
          õppuritele, õpetajatele ning kõigile huvilistele hõlpsasti leitavaks.
          Tulemuste juures võib olla ka lisateavet, näiteks ülesanded,
          lahendused ja võistluse kirjeldus.
        </p>
        <p>
          Andmete täiendamise ja küsimuste korral kirjuta meile:{" "}
          <a href="mailto:eoakontakt@gmail.com">eoakontakt@gmail.com</a>.
        </p>
      </section>
    </>
  );
}
