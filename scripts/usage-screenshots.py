#!/usr/bin/env python3
"""Generate the screenshots used on the Usage examples page.

The script logs in to the FDP client as the default admin, creates the records it
needs through the API, walks through the client, draws a red box around the element
the reader has to use, and saves one PNG per step in docs/usage/images.

Requirements

    pip install playwright
    python -m playwright install chromium

    A freshly started ``fdp/ephemeral/v1`` stack from https://github.com/FAIRDataTeam/compose,
    with the client on http://localhost and the API on http://localhost:8080.
    The script does not clean up after itself, so run it on a fresh stack.

Usage

    python scripts/usage-screenshots.py [--client URL] [--api URL] [--out DIR]
"""

import argparse
import json
import pathlib
import sys
import urllib.request

from playwright.sync_api import Page, Locator, sync_playwright

ADMIN = {"email": "albert.einstein@example.com", "password": "password"}

VIEWPORT = {"width": 1200, "height": 760}
SCALE = 1.5

HIGHLIGHT_JS = """
(els) => {
  for (const el of els) {
    el.style.outline = '3px solid #d7263d';
    el.style.outlineOffset = '4px';
    el.style.boxShadow = '0 0 0 8px rgba(215, 38, 61, 0.18)';
    if (!el.style.borderRadius) { el.style.borderRadius = '4px'; }
  }
}
"""

# Example content, so that the screenshots resemble an FDP in use rather than a fresh deployment.
PREFIXES = """
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix fdp-o: <https://w3id.org/fdp/fdp-o#> .
"""

ROOT_TTL = PREFIXES + """
<> a fdp-o:FAIRDataPoint, fdp-o:MetadataService, dcat:DataService, dcat:Resource ;
    dct:title "Example University FAIR Data Point" ;
    dct:description "Metadata of the research datasets and software published by the research groups of Example University. Each catalog belongs to an institute, which maintains its own entries." ;
    dcat:version "1.0" ;
    dct:publisher [ a foaf:Agent ; foaf:name "Example University Library" ] ;
    dcat:endpointURL <{api}> ;
    dcat:endpointDescription <{api}/v3/api-docs>, <{api}/swagger-ui.html> .
"""

PUBLISHED_CATALOG_TTL = PREFIXES + """
<> a dcat:Catalog ;
    dct:title "Institute for Climate Studies" ;
    dct:description "Observational and model data of the Institute for Climate Studies, including the long-term measurement series of the Example Valley field station." ;
    dcat:version "2.3" ;
    dct:publisher [ a foaf:Agent ; foaf:name "Institute for Climate Studies, Example University" ] ;
    dct:isPartOf <{api}> .
"""

DRAFT_CATALOG_TTL = PREFIXES + """
<> a dcat:Catalog ;
    dct:title "Materials Science Laboratory" ;
    dct:description "Measurement data and analysis software of the Materials Science Laboratory, starting with the 2026 thin film experiments." ;
    dcat:version "1.0" ;
    dct:publisher [ a foaf:Agent ; foaf:name "Materials Science Laboratory, Example University" ] ;
    dct:isPartOf <{api}> .
"""

DATASET_TTL = PREFIXES + """
<> a dcat:Dataset ;
    dct:title "Example Valley air temperature, 1996-2025" ;
    dct:description "Hourly air temperature measured at the Example Valley field station." ;
    dcat:version "1.2" ;
    dct:publisher [ a foaf:Agent ; foaf:name "Institute for Climate Studies, Example University" ] ;
    dcat:theme <http://www.wikidata.org/entity/Q11466> ;
    dcat:keyword "temperature", "field station" ;
    dct:isPartOf <{catalog}> .
"""

SOFTWARE_SHAPE = """@prefix : <http://fairdatapoint.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix schema: <https://schema.org/> .

:SoftwareShape a sh:NodeShape ;
    sh:targetClass schema:SoftwareSourceCode ;
    sh:property [
        sh:path schema:codeRepository ;
        sh:nodeKind sh:IRI ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        dash:editor dash:URIEditor ;
        dash:viewer dash:URIViewer ;
        sh:order 30 ;
    ], [
        sh:path schema:programmingLanguage ;
        sh:nodeKind sh:Literal ;
        dash:editor dash:TextFieldEditor ;
        dash:viewer dash:LiteralViewer ;
        sh:order 31 ;
    ] .
"""


class Api:
    """Minimal client for the FDP API, used to prepare records."""

    def __init__(self, base):
        self.base = base.rstrip("/")
        self.token = self.call("POST", "/tokens", ADMIN)["token"]

    def call(self, method, path, body=None, content_type="application/json", raw=False):
        data = None
        headers = {"Accept": "text/turtle" if content_type == "text/turtle" else "application/json"}
        if body is not None:
            data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
            headers["Content-Type"] = content_type
        if getattr(self, "token", None):
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        with urllib.request.urlopen(req) as res:
            if raw:
                return res
            text = res.read().decode()
            return json.loads(text) if text else None

    def create_record(self, prefix, turtle):
        res = self.call("POST", f"/{prefix}", turtle, content_type="text/turtle", raw=True)
        return res.headers["Location"]

    def publish(self, record):
        path = record[len(self.base):] or "/"
        self.call("PUT", path.rstrip("/") + "/meta/state", {"current": "PUBLISHED"})

    def seed(self):
        """Replace the default root record and add catalogs, so the screenshots show an FDP in use."""
        self.call("PUT", "/", ROOT_TTL.format(api=self.base), content_type="text/turtle", raw=True)
        settings = self.call("GET", "/settings")
        self.call("PUT", "/settings", {
            "appTitle": "Example University", "appSubtitle": "FAIR Data Point",
            "metadataMetrics": settings["metadataMetrics"],
            "ping": {"enabled": settings["ping"]["enabled"], "endpoints": settings["ping"]["endpoints"]},
            "search": settings["search"], "forms": settings["forms"],
        })
        published = self.create_record("catalog", PUBLISHED_CATALOG_TTL.format(api=self.base))
        dataset = self.create_record("dataset", DATASET_TTL.format(catalog=published))
        self.publish(published)
        self.publish(dataset)
        return self.create_record("catalog", DRAFT_CATALOG_TTL.format(api=self.base))

    def schema_uuid(self, name):
        return next(s["uuid"] for s in self.call("GET", "/metadata-schemas") if s["name"] == name)

    def resource_definition(self, url_prefix):
        return next(r for r in self.call("GET", "/resource-definitions") if r["urlPrefix"] == url_prefix)


class Shots:
    def __init__(self, page: Page, out: pathlib.Path, client: str):
        self.page = page
        self.out = out
        self.client = client.rstrip("/")

    def goto(self, path):
        self.page.goto(self.client + path)
        self.page.wait_for_load_state("networkidle")

    def highlight(self, *locators: Locator):
        for loc in locators:
            loc.first.wait_for()
            loc.evaluate_all(HIGHLIGHT_JS)

    def save(self, name, focus: Locator = None, align_top=False, height=None):
        """Screenshot the viewport, scrolled so that ``focus`` is visible.

        With ``align_top`` the focused element is placed near the top of the
        viewport, and ``height`` temporarily changes the viewport height.
        """
        if height:
            self.page.set_viewport_size({"width": VIEWPORT["width"], "height": height})
        if focus is not None:
            if align_top:
                focus.first.evaluate("el => { el.scrollIntoView({block: 'start'}); window.scrollBy(0, -24); }")
            else:
                focus.first.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)
        path = self.out / f"{name}.png"
        self.page.screenshot(path=str(path))
        print("saved", path)
        if height:
            self.page.set_viewport_size(VIEWPORT)

    def login(self):
        self.goto("/login")
        form = self.page.locator("form", has=self.page.locator("[data-cy=login]"))
        form.locator("input").nth(0).fill(ADMIN["email"])
        form.locator("input").nth(1).fill(ADMIN["password"])
        form.locator("[data-cy=login]").click()
        self.page.wait_for_url(self.client + "/")
        self.page.wait_for_load_state("networkidle")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client", default="http://localhost")
    parser.add_argument("--api", default="http://localhost:8080")
    parser.add_argument("--out", default=pathlib.Path(__file__).resolve().parent.parent / "docs/usage/images")
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    api = Api(args.api)
    catalog = api.seed()
    catalog_uuid = catalog.rsplit("/", 1)[1]
    print("draft catalog", catalog)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=SCALE)
        page = context.new_page()
        page.set_default_timeout(20000)
        s = Shots(page, out, args.client)
        s.login()

        # 1. home page, Create next to the list of catalogs
        s.goto("/")
        catalogs = page.locator(".item-list", has_text="Catalogs")
        create = catalogs.locator("[data-cy=create]")
        s.highlight(create)
        s.save("home-create-catalog", create)

        # 2. catalog page of a draft, Publish
        s.goto(f"/catalog/{catalog_uuid}")
        publish = page.locator("[data-cy=publish]")
        s.highlight(publish)
        s.save("catalog-publish", publish)

        # 3. metadata schemas list, + Create, Import, Update
        s.goto("/schemas")
        s.highlight(
            page.locator("[data-cy=create-schema]"),
            page.locator("[data-cy=import-schemas]"),
            page.locator("[data-cy=update-schemas]"),
        )
        s.save("schemas-list")

        # 4. new schema form, filled for the Software type, Save and release
        s.goto("/schemas/create")
        page.fill("#name", "Software")
        page.fill("#description", "Research software, described with schema.org terms")
        page.locator("[data-cy=add-shape]").click()
        page.locator("[data-cy=target-class] select").last.select_option(label="Resource")
        page.fill("#suggestedResourceName", "Software")
        page.fill("#suggestedUrlPrefix", "software")
        # the definition editor is a contenteditable element that updates its model on key events
        page.locator("#schema-definition pre").evaluate(
            """(el, text) => {
                el.innerText = text;
                el.dispatchEvent(new InputEvent('input', {bubbles: true}));
                el.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
            }""",
            SOFTWARE_SHAPE,
        )
        extends = page.locator("[data-cy=target-class]").last
        s.highlight(extends)
        s.save("schema-form", page.locator("#name"), align_top=True, height=900)
        save_release = page.locator("[data-cy=save-release]")
        s.highlight(save_release)
        s.save("schema-form-save", save_release)
        save_release.click()
        page.wait_for_url("**/schemas/*/release")
        page.wait_for_load_state("networkidle")

        # 5. release page, version, Public version, Release
        page.fill("#description", "First version")
        page.fill("#major", "1")
        page.fill("#minor", "0")
        page.fill("#patch", "0")
        public = page.locator("label", has_text="Public version")
        release = page.locator("button", has_text="Release")
        s.highlight(public, release)
        s.save("schema-release", release)
        release.click()
        page.wait_for_load_state("networkidle")

        # 6. resource definitions list, + Create resource definition
        s.goto("/resource-definitions")
        create_rd = page.locator("[data-cy=create-resourceDefinition]")
        s.highlight(create_rd)
        s.save("resource-definitions-list", create_rd)

        # The Software resource definition itself is created through the API,
        # so that the screenshot of the Catalog definition can show it as a child.
        software_schema = api.schema_uuid("Software")
        api.call("POST", "/resource-definitions", {
            "name": "Software", "urlPrefix": "software",
            "metadataSchemaUuids": [software_schema], "children": [],
            "externalLinks": [{"title": "Code repository", "propertyUri": "https://schema.org/codeRepository"}],
        })

        # 7. Catalog resource definition, add Software as a child, Save
        catalog_rd = api.resource_definition("catalog")
        s.goto(f"/resource-definitions/{catalog_rd['uuid']}")
        page.locator("[data-cy=add-child]").click()
        child = page.locator("[data-cy=child]").last
        child.locator("select").first.select_option(label="Software")
        inputs = child.locator("input")
        inputs.nth(0).fill("http://www.w3.org/ns/dcat#resource")
        inputs.nth(1).fill("Software")
        save = page.locator("[data-cy=save]")
        s.highlight(child, save)
        s.save("catalog-definition-children", child, align_top=True, height=1000)
        save.click()
        page.wait_for_load_state("networkidle")

        # 8. catalog settings, add a member
        s.goto(f"/catalog/{catalog_uuid}/settings")
        invite = page.locator("form.form--inline", has=page.locator("#user-role"))
        s.highlight(invite)
        s.save("catalog-settings-members", invite)

        # 9. user menu, API Keys
        s.goto("/")
        page.locator("[data-cy=user-menu] button").click()
        api_keys = page.locator(".dropdown-menu.show a.dropdown-item", has_text="API Keys")
        s.highlight(api_keys)
        s.save("user-menu-api-keys")

        # 10. settings, FDP Index connection
        s.goto("/settings")
        heading = page.locator("h2", has_text="FDP Index connection")
        add_index = page.locator("label", has_text="Connected FDP Indexes").locator("xpath=following::button[1]")
        s.highlight(heading, add_index)
        s.save("settings-fdp-index", heading, align_top=True, height=640)

        browser.close()


if __name__ == "__main__":
    sys.exit(main())
