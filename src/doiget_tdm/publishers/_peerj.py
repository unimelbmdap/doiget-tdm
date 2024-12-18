from __future__ import annotations

import doiget_tdm.publisher
import doiget_tdm.metadata


@doiget_tdm.publisher.add_publisher
class PeerJ(
    doiget_tdm.publisher.GenericWebHost,
    doiget_tdm.publisher.Publisher,
):

    member_id = doiget_tdm.metadata.MemberID(id_="4443")

    # the server returns an X-RateLimit-Limit header, which could
    # be used to set custom rate limits
