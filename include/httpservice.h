#ifndef _HTTPSERVICE_
#define _HTTPSERVICE_

#include "instance.h"

#include "rlw32compat.h"

/*
 * libcurl is used by the desktop builds.  The Android player deliberately
 * keeps the native binary self-contained, so it can be built with
 * OPENRBLX_NO_CURL and use the local place bundled in the APK.
 */
#ifndef OPENRBLX_NO_CURL
#include <curl/curl.h>
#endif

#include "cJSON.h"

typedef enum {
    HttpContentType_ApplicationJson,
    HttpContentType_ApplicationXml,
    HttpContentType_ApplicationUrlEncoded,
    HttpContentType_TextPlain,
    HttpContentType_TextXml,
} HttpContentType;

typedef struct HttpService {
    Instance instance;

#ifndef OPENRBLX_NO_CURL
    CURL *curl;
#else
    void *curl;
#endif
} HttpService;

HttpService *HttpService_new(const char *className, Instance *parent);

const char *HttpService_GetAsync(HttpService *this, const char *url, int *dataSize);
const char *HttpService_PostAsync(HttpService *this, const char *url, const char *data, HttpContentType contentType);

cJSON *HttpService_JSONDecode(HttpService *this, const char *input);
const char *HttpService_JSONEncode(HttpService *this, cJSON *input);

void serialize_HttpService(HttpService *httpservice, SerializeInstance *inst);

#endif
