"""Receipt model and the planted set. Formatters only print; they do not settle GST."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

Kind = Literal["item", "alcohol", "service", "tip", "promo", "rounding"]
GstMode = Literal["inclusive", "exclusive", "none"]
Category = Literal["meals", "transport", "equipment", "accommodation", "other"]

GST_RATE = Decimal("0.09")
GST_INCL_NUM = Decimal(9)
GST_INCL_DEN = Decimal(109)
TWOPLACES = Decimal("0.01")
CLAIM_START = date(2026, 3, 1)
CLAIM_END = date(2026, 7, 31)
COLUMNS = ("receipt_id", "date", "vendor", "category", "total", "gst")
CATEGORIES = ("meals", "transport", "equipment", "accommodation", "other")


def money(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def fmt_money(value: Decimal) -> str:
    return f"{money(value):.2f}"


@dataclass
class LineItem:
    desc: str
    amount: Decimal
    kind: Kind = "item"


@dataclass
class Receipt:
    receipt_id: str
    date: date
    vendor: str
    category: Category
    source: int
    items: list[LineItem]
    gst_mode: GstMode
    gst_reg: str | None
    flags: set[str] = field(default_factory=set)
    paid: Decimal = Decimal(0)
    gst: Decimal | None = None
    time: str = ""
    pickup: str = ""
    dropoff: str = ""
    tendered: Decimal | None = None
    loyalty_pts: int | None = None
    you_saved: Decimal | None = None
    date_printed: str = ""
    amount_printed: str = ""
    quoted_reply: bool = False
    address: str = ""
    payment: str = "NETS"
    print_date: date | None = None

    @property
    def claimable(self) -> bool:
        return not (self.flags & {"void", "reprint", "extra", "skip"})

    @property
    def subtotal(self) -> Decimal:
        return money(sum((item.amount for item in self.items), Decimal(0)))


def settle(receipt: Receipt) -> Receipt:
    """Set paid and gst from items + gst_mode + gst_reg. Inclusive: gst = paid * 9 / 109."""
    subtotal = receipt.subtotal
    if receipt.gst_mode == "inclusive":
        receipt.paid = subtotal
        receipt.gst = (
            money(receipt.paid * GST_INCL_NUM / GST_INCL_DEN)
            if receipt.gst_reg
            else None
        )
    elif receipt.gst_mode == "exclusive":
        printed = money(subtotal * GST_RATE)
        receipt.paid = money(subtotal + printed)
        receipt.gst = printed if receipt.gst_reg else None
    else:
        receipt.paid = subtotal
        receipt.gst = None
    return receipt


def _item(desc: str, amount: str, kind: Kind = "item") -> LineItem:
    return LineItem(desc=desc, amount=money(amount), kind=kind)


def make(
    receipt_id: str,
    day: date,
    vendor: str,
    category: Category,
    source: int,
    items: list[LineItem],
    gst_mode: GstMode,
    gst_reg: str | None,
    flags: set[str] | None = None,
    **kwargs: object,
) -> Receipt:
    receipt = Receipt(
        receipt_id=receipt_id,
        date=day,
        vendor=vendor,
        category=category,
        source=source,
        items=items,
        gst_mode=gst_mode,
        gst_reg=gst_reg,
        flags=set(flags or ()),
        **kwargs,  # type: ignore[arg-type]
    )
    return settle(receipt)


def as_reprint(receipt: Receipt) -> Receipt:
    copy = Receipt(
        receipt_id=receipt.receipt_id,
        date=receipt.date,
        vendor=receipt.vendor,
        category=receipt.category,
        source=receipt.source,
        items=list(receipt.items),
        gst_mode=receipt.gst_mode,
        gst_reg=receipt.gst_reg,
        flags=set(receipt.flags) | {"reprint"},
        paid=receipt.paid,
        gst=receipt.gst,
        time=receipt.time,
        pickup=receipt.pickup,
        dropoff=receipt.dropoff,
        tendered=receipt.tendered,
        loyalty_pts=receipt.loyalty_pts,
        you_saved=receipt.you_saved,
        date_printed=receipt.date_printed,
        amount_printed=receipt.amount_printed,
        quoted_reply=receipt.quoted_reply,
        address=receipt.address,
        payment=receipt.payment,
        print_date=receipt.print_date,
    )
    return copy


REG_KOPI = "201908877K"
REG_NIGHT = "201512220N"
REG_BISTRO = "201704412B"
REG_CIRCUIT = "200833901C"
REG_HARBOUR = "202312345M"
REG_ORCHARD = "199904118H"
REG_BYTE = "201611002E"
REG_STUDIO = "201822773S"


def planted() -> list[Receipt]:
    """Every receipt in the dataset. A missing flag here is a missing trap."""
    rows: list[Receipt] = []

    # source 01 -- thermal. reprint original + near-dupe pair.
    r1042 = make(
        "R-1042",
        date(2026, 6, 8),
        "KOPI HOR PTE LTD",
        "meals",
        1,
        [
            _item("KOPI", "2.00"),
            _item("KAYA TOAST", "4.50"),
            _item("NASI LEMAK", "12.00"),
        ],
        "inclusive",
        REG_KOPI,
        flags={"reprint_original", "near_dupe"},
        time="08:42",
        address="12 TELOK AYER ST",
    )
    rows.append(r1042)
    rows.append(as_reprint(r1042))
    rows.append(
        make(
            "R-1188",
            date(2026, 6, 15),
            "KOPI HOR PTE LTD",
            "meals",
            1,
            [
                _item("KOPI", "2.00"),
                _item("KAYA TOAST", "4.50"),
                _item("NASI LEMAK", "12.00"),
            ],
            "inclusive",
            REG_KOPI,
            flags={"near_dupe"},
            time="08:51",
            address="12 TELOK AYER ST",
        )
    )
    rows.append(
        make(
            "R-1201",
            date(2026, 6, 10),
            "NIGHT OWL SUPERMART",
            "other",
            1,
            [_item("PRINTER PAPER 2PK", "24.00")],
            "inclusive",
            REG_NIGHT,
            flags={"void"},
            time="21:14",
            address="88 LAVENDER ST",
        )
    )
    rows.append(
        make(
            "R-1210",
            date(2026, 6, 12),
            "AH HUAT CHICKEN RICE",
            "meals",
            1,
            [_item("CHICKEN RICE", "6.50"), _item("TEH C", "1.80")],
            "inclusive",
            "M90123456X",
            flags={"noise"},
            time="12:18",
            address="MAXWELL FOOD CENTRE #01-14",
            tendered=money("10.00"),
            loyalty_pts=420,
            you_saved=money("1.20"),
        )
    )
    rows.append(
        make(
            "R-1220",
            date(2026, 6, 20),
            "NIGHT OWL SUPERMART",
            "other",
            1,
            [
                _item("FRESH MILK 1L", "3.50"),
                _item("WHITE BREAD", "2.80"),
                _item("EGGS 10S", "3.70"),
                _item("ROUNDING ADJ", "-0.02", "rounding"),
            ],
            "inclusive",
            REG_NIGHT,
            flags={"rounding"},
            time="19:03",
            address="88 LAVENDER ST",
        )
    )
    rows.append(
        make(
            "R-1301",
            date(2026, 6, 18),
            "LITTLE PENINSULA BISTRO",
            "meals",
            1,
            [
                _item("SET LUNCH", "48.00"),
                _item("HOUSE RED 150ML", "22.00", "alcohol"),
                _item("SERVICE 10%", "7.00", "service"),
            ],
            "inclusive",
            REG_BISTRO,
            flags={"service", "alcohol"},
            time="13:22",
            address="5 ANN SIANG RD",
        )
    )
    rows.append(
        make(
            "R-1401",
            date(2026, 6, 25),
            "CIRCUIT MART ELECTRONICS",
            "equipment",
            1,
            [_item("USB WEBCAM", "189.00"), _item("HDMI CAPTURE", "261.00")],
            "inclusive",
            REG_CIRCUIT,
            flags={"equipment_mid"},
            time="16:40",
            address="FUMANAN CENTRE 03-18",
            payment="VISA",
        )
    )
    rows.append(
        make(
            "R-1501",
            date(2026, 6, 22),
            "MAXWELL STALL 14",
            "meals",
            1,
            [
                _item("LAKSA", "7.50"),
                _item("FRIED PRAWN", "8.00"),
                _item("BANDUNG", "4.30"),
            ],
            "inclusive",
            "M91220011X",
            flags={"per_day"},
            time="12:05",
            address="MAXWELL FOOD CENTRE",
        )
    )
    rows.append(
        make(
            "R-1502",
            date(2026, 6, 22),
            "KOPI HOR PTE LTD",
            "meals",
            1,
            [_item("LUNCHEON SET", "16.50")],
            "inclusive",
            REG_KOPI,
            flags={"per_day"},
            time="13:10",
            address="12 TELOK AYER ST",
        )
    )
    rows.append(
        make(
            "R-1601",
            date(2026, 7, 8),
            "LITTLE PENINSULA BISTRO",
            "meals",
            1,
            [
                _item("DINNER MAINS", "24.00"),
                _item("SIDES", "10.09"),
                _item("SERVICE 10%", "3.41", "service"),
            ],
            "inclusive",
            REG_BISTRO,
            flags={"post_july"},
            time="19:48",
            address="5 ANN SIANG RD",
        )
    )
    rows.append(
        make(
            "R-1701",
            date(2026, 6, 3),
            "AH HUAT CHICKEN RICE",
            "meals",
            1,
            [_item("CHICKEN RICE", "5.50"), _item("TEH O", "1.70")],
            "none",
            None,
            time="11:55",
            address="MAXWELL FOOD CENTRE #01-14",
        )
    )
    rows.append(
        make(
            "R-1702",
            date(2026, 6, 28),
            "AH HUAT CHICKEN RICE",
            "meals",
            1,
            [_item("ROAST CHICKEN", "7.00"), _item("BARLEY", "2.40")],
            "none",
            None,
            time="12:40",
            address="MAXWELL FOOD CENTRE #01-14",
        )
    )
    rows.append(
        make(
            "R-1703",
            date(2026, 7, 2),
            "NIGHT OWL SUPERMART",
            "other",
            1,
            [
                _item("AA BATTERIES", "6.80"),
                _item("MASKING TAPE", "4.20"),
                _item("ZIP BAGS", "4.60"),
            ],
            "inclusive",
            REG_NIGHT,
            time="20:11",
            address="88 LAVENDER ST",
        )
    )
    rows.append(
        make(
            "R-1704",
            date(2026, 7, 14),
            "CIRCUIT MART ELECTRONICS",
            "equipment",
            1,
            [_item("USB-C HUB", "89.00")],
            "inclusive",
            REG_CIRCUIT,
            time="15:02",
            address="FUMANAN CENTRE 03-18",
            payment="NETS",
        )
    )

    # source 02 -- e-receipt emails.
    rows.append(
        make(
            "TXN88201",
            date(2026, 6, 19),
            "Harbour View Cafe PTE LTD",
            "meals",
            2,
            [_item("Dinner for two", "42.00")],
            "exclusive",
            None,
            flags={"no_gst_reg"},
            time="21:04",
            address="44 Boat Quay",
            quoted_reply=True,
            payment="VISA",
            print_date=date(2026, 6, 20),
        )
    )
    rows.append(
        make(
            "TXN88250",
            date(2026, 6, 11),
            "Riverview Inn",
            "accommodation",
            2,
            [_item("Room 1 night", "180.00")],
            "exclusive",
            None,
            flags={"no_gst_reg"},
            time="10:12",
            address="17 Robertson Quay",
            payment="VISA",
        )
    )
    rows.append(
        make(
            "TXN88300",
            date(2026, 7, 3),
            "Harbour View Cafe PTE LTD",
            "meals",
            2,
            [_item("Weekday lunch", "28.00")],
            "exclusive",
            REG_HARBOUR,
            flags={"gst_excl"},
            time="13:18",
            address="44 Boat Quay",
            quoted_reply=True,
            payment="Mastercard",
        )
    )
    rows.append(
        make(
            "TXN89001",
            date(2026, 7, 5),
            "Studio Kit House PTE LTD",
            "equipment",
            2,
            [_item("4K field monitor", "1280.00")],
            "exclusive",
            REG_STUDIO,
            flags={"equipment_high"},
            time="11:30",
            address="81 Playfair Rd",
            payment="VISA",
        )
    )
    rows.append(
        make(
            "TXN88410",
            date(2026, 6, 4),
            "Orchard Stay Hotel",
            "accommodation",
            2,
            [_item("Deluxe 1 night", "220.00")],
            "exclusive",
            REG_ORCHARD,
            time="09:05",
            address="328 Orchard Rd",
            payment="VISA",
        )
    )
    rows.append(
        make(
            "TXN88420",
            date(2026, 6, 27),
            "Harbour View Cafe PTE LTD",
            "meals",
            2,
            [_item("Team brunch", "24.00")],
            "exclusive",
            REG_HARBOUR,
            time="11:40",
            address="44 Boat Quay",
            payment="NETS",
        )
    )
    rows.append(
        make(
            "TXN88430",
            date(2026, 7, 11),
            "Byte Bazaar PTE LTD",
            "equipment",
            2,
            [_item("Wireless presenter", "156.00")],
            "exclusive",
            REG_BYTE,
            time="14:22",
            address="Sim Lim Square 02-88",
            payment="NETS",
        )
    )

    # source 03 -- ride-hailing. HN-03 is the claimable half of the cross-dupe.
    rows.append(
        make(
            "HN-03",
            date(2026, 6, 22),
            "GoRide",
            "transport",
            3,
            [
                _item("Fare", "11.20"),
                _item("Surge 1.3x", "2.40"),
                _item("Platform fee", "0.40"),
                _item("Tip", "2.00", "tip"),
                _item("Promo", "-1.20", "promo"),
            ],
            "none",
            None,
            flags={"cross_dupe", "tip"},
            time="19:14",
            pickup="1 Fusionopolis Way",
            dropoff="Tanjong Pagar MRT",
            payment="WALLET",
        )
    )
    rows.append(
        make(
            "HN-07",
            date(2026, 6, 9),
            "GoRide",
            "transport",
            3,
            [
                _item("Fare", "8.50"),
                _item("Platform fee", "0.40"),
                _item("Tip", "3.00", "tip"),
            ],
            "none",
            None,
            flags={"tip"},
            time="08:22",
            pickup="Lavender MRT",
            dropoff="Raffles Place",
            payment="WALLET",
        )
    )
    rows.append(
        make(
            "HN-08",
            date(2026, 7, 1),
            "GoRide",
            "transport",
            3,
            [
                _item("Fare", "15.00"),
                _item("Surge 1.2x", "3.00"),
                _item("Platform fee", "0.40"),
                _item("Promo", "-4.00", "promo"),
            ],
            "none",
            None,
            time="18:05",
            pickup="HarbourFront",
            dropoff="Bugis Junction",
            payment="VISA",
        )
    )
    rows.append(
        make(
            "HN-12",
            date(2026, 6, 5),
            "GoRide",
            "transport",
            3,
            [_item("Fare", "8.80"), _item("Platform fee", "0.40")],
            "none",
            None,
            time="09:10",
            pickup="Outram Park",
            dropoff="Tanjong Pagar",
            payment="WALLET",
        )
    )
    rows.append(
        make(
            "HN-14",
            date(2026, 6, 16),
            "GoRide",
            "transport",
            3,
            [
                _item("Fare", "18.00"),
                _item("Surge 1.2x", "4.00"),
                _item("Platform fee", "0.40"),
            ],
            "none",
            None,
            time="22:41",
            pickup="Clarke Quay",
            dropoff="Serangoon",
            payment="WALLET",
        )
    )
    rows.append(
        make(
            "HN-16",
            date(2026, 7, 12),
            "GoRide",
            "transport",
            3,
            [_item("Fare", "7.40"), _item("Platform fee", "0.40")],
            "none",
            None,
            time="10:33",
            pickup="City Hall",
            dropoff="Bugis",
            payment="WALLET",
        )
    )
    rows.append(
        make(
            "HN-18",
            date(2026, 7, 20),
            "GoRide",
            "transport",
            3,
            [_item("Fare", "18.20"), _item("Platform fee", "0.40")],
            "none",
            None,
            time="17:55",
            pickup="Paya Lebar",
            dropoff="Raffles Place",
            payment="WALLET",
        )
    )
    rows.append(
        make(
            "HN-21",
            date(2026, 3, 15),
            "GoRide",
            "transport",
            3,
            [_item("Fare", "12.10"), _item("Platform fee", "0.40")],
            "none",
            None,
            time="08:05",
            pickup="Redhill",
            dropoff="Tanjong Pagar",
            payment="WALLET",
        )
    )

    # source 04 -- handwritten. 03/04/2026 is 3 April. 27/03/2026 is the DD/MM tell.
    rows.append(
        make(
            "hawkers 3/4",
            date(2026, 4, 3),
            "hawker lunch",
            "meals",
            4,
            [_item("hawker lunch", "12.50")],
            "none",
            None,
            flags={"ambiguous_date"},
            date_printed="03/04/2026",
            amount_printed="12.5",
        )
    )
    rows.append(
        make(
            "taxi 27/3",
            date(2026, 3, 27),
            "taxi to client",
            "transport",
            4,
            [_item("taxi to client", "18.00")],
            "none",
            None,
            flags={"date_tell"},
            date_printed="27/03/2026",
            amount_printed="S$18.00",
        )
    )
    rows.append(
        make(
            "taxis 3/4",
            date(2026, 6, 22),
            "goride",
            "transport",
            4,
            [_item("goride taxi", "15.00")],
            "none",
            None,
            flags={"cross_dupe", "skip"},
            date_printed="22/6",
            amount_printed="15",
        )
    )
    rows.append(
        make(
            "PeakDesk 8/6",
            date(2026, 6, 8),
            "PeakDesk Co-Working",
            "other",
            4,
            [_item("day pass", "35.00")],
            "none",
            None,
            flags={"gap"},
            date_printed="8/6",
            amount_printed="35",
        )
    )
    rows.append(
        make(
            "mrt Jun",
            date(2026, 6, 2),
            "simplygo topup",
            "transport",
            4,
            [_item("simplygo", "20.00")],
            "none",
            None,
            date_printed="2 Jun",
            amount_printed="20",
        )
    )
    rows.append(
        make(
            "usb hub",
            date(2026, 6, 30),
            "sim lim spare hub",
            "equipment",
            4,
            [_item("usb hub", "16.00")],
            "none",
            None,
            date_printed="30/6",
            amount_printed="S$16",
        )
    )
    rows.append(
        make(
            "supper 4/7",
            date(2026, 7, 4),
            "prata 3am",
            "meals",
            4,
            [_item("prata", "11.00")],
            "none",
            None,
            date_printed="4/7",
            amount_printed="11",
        )
    )

    # source 05 -- hotel folio. Not in ground truth.
    rows.append(
        make(
            "FOLIO-11",
            date(2026, 6, 14),
            "Riverview Inn",
            "accommodation",
            5,
            [
                _item("Room 14-15 Jun", "320.00"),
                _item("Minibar", "18.00"),
                _item("GST 9%", "30.42"),
            ],
            "none",
            "201033441R",
            flags={"extra"},
            time="12:00",
            address="17 Robertson Quay",
            payment="VISA",
        )
    )
    return rows
