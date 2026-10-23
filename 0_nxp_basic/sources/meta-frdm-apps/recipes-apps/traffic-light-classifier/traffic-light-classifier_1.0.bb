SUMMARY = "HSV-based traffic light classifier (red/yellow/green)"
LICENSE = "CLOSED"

SRC_URI = "file://traffic_light_classifier.py"
S = "${WORKDIR}"

inherit allarch

RDEPENDS:${PN} = "python3-core python3-numpy python3-opencv"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/traffic_light_classifier.py ${D}${bindir}/traffic-light-classifier
}
