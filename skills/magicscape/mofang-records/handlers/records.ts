/**
 * mofang_query_records — 查询记录
 * mofang_create_record — 创建记录
 * mofang_update_record — 修改记录
 * mofang_delete_record — 删除记录
 *
 * 所有 handler 接受 formHint + spaceHint，内部自动 resolve + 字段映射
 */

import { apiRequest, type HttpClientConfig } from './utils/http-client.js';
import {
  buildEncodedBq,
  type BqFilter,
  type BqOrderBy,
  type BuildBqOptions,
} from './utils/bq-builder.js';
import { resolveSpaceForm } from './utils/resolve.js';
import {
  fetchFieldDefs,
  mapDataKeys,
  mapFilterFieldNames,
  buildFieldMaps,
  type FieldDef,
} from './utils/field-defs.js';

function buildConfig(context: { config: Record<string, string> }): HttpClientConfig {
  return {
    baseUrl: context.config.BASE_URL,
    username: context.config.USERNAME,
    password: context.config.PASSWORD,
  };
}

// ============ 查询记录 ============

export interface QueryRecordsParams {
  formHint: string;
  spaceHint?: string;
  page?: number;
  pageSize?: number;
  all?: boolean;
  filters?: BqFilter[];
  orderBy?: BqOrderBy;
}

export interface QueryRecordsResult {
  success: boolean;
  message: string;
  data?: {
    totalCount: number;
    records: Record<string, any>[];
    fieldLabels?: Record<string, string>;
  };
  spaceLabel?: string;
  formLabel?: string;
}

export async function queryRecordsHandler(
  params: QueryRecordsParams,
  context: { config: Record<string, string> }
): Promise<QueryRecordsResult> {
  const config = buildConfig(context);

  if (!config.baseUrl) {
    return { success: false, message: '未配置 BASE_URL。' };
  }

  const resolved = await resolveSpaceForm(config, params.formHint, params.spaceHint);
  if (!resolved.success || !resolved.spaceId || !resolved.formId) {
    return { success: false, message: resolved.message };
  }

  const { spaceId, formId } = resolved;

  // 获取字段定义用于 filter 映射和返回 fieldLabels
  const fieldResult = await fetchFieldDefs(config, spaceId, formId);
  let fieldLabels: Record<string, string> | undefined;
  let resolvedFilters = params.filters;

  if (fieldResult.success && fieldResult.fields.length > 0) {
    const { nameToLabel } = buildFieldMaps(fieldResult.fields);
    fieldLabels = Object.fromEntries(nameToLabel);

    if (params.filters && params.filters.length > 0) {
      const { mapped } = mapFilterFieldNames(fieldResult.fields, params.filters);
      resolvedFilters = mapped;
    }
  }

  const page = params.page ?? 1;
  const pageSize = params.pageSize ?? 10;
  const useAll = params.all ?? false;

  const start = useAll ? 0 : (page - 1) * pageSize;
  const limit = useAll ? -1 : pageSize;

  const bqOptions: BuildBqOptions = {
    filters: resolvedFilters,
    orderBy: params.orderBy,
  };
  const encodedBq = buildEncodedBq(bqOptions);

  let path = `/magicflu/service/s/jsonv2/${spaceId}/forms/${formId}/records/entry?start=${start}&limit=${limit}`;
  if (encodedBq) {
    path += `&bq=${encodedBq}`;
  }

  const result = await apiRequest(config, 'GET', path);

  if (!result.success) {
    return { success: false, message: `记录查询失败: ${result.message}` };
  }

  const entries = result.data?.entry;
  const totalCount = result.data?.totalCount ?? 0;
  const records = Array.isArray(entries) ? entries : [];

  return {
    success: true,
    message: `表单「${resolved.formLabel}」查询到 ${totalCount} 条记录（当前返回 ${records.length} 条）。`,
    data: { totalCount, records, fieldLabels },
    spaceLabel: resolved.spaceLabel,
    formLabel: resolved.formLabel,
  };
}

// ============ 创建记录 ============

export interface CreateRecordParams {
  formHint: string;
  spaceHint?: string;
  data: Record<string, any>;
}

export interface MutationResult {
  success: boolean;
  message: string;
  data?: {
    errcode: string;
    errmsg: string;
    id?: string;
  };
  spaceLabel?: string;
  formLabel?: string;
}

export async function createRecordHandler(
  params: CreateRecordParams,
  context: { config: Record<string, string> }
): Promise<MutationResult> {
  const config = buildConfig(context);

  if (!config.baseUrl) {
    return { success: false, message: '未配置 BASE_URL。' };
  }

  if (!params.data || Object.keys(params.data).length === 0) {
    return { success: false, message: '记录数据不能为空。' };
  }

  const resolved = await resolveSpaceForm(config, params.formHint, params.spaceHint);
  if (!resolved.success || !resolved.spaceId || !resolved.formId) {
    return { success: false, message: resolved.message };
  }

  const { spaceId, formId } = resolved;

  const fieldResult = await fetchFieldDefs(config, spaceId, formId);
  let submitData = params.data;
  if (fieldResult.success && fieldResult.fields.length > 0) {
    const { mapped, warnings } = mapDataKeys(fieldResult.fields, params.data);
    submitData = mapped;
    if (warnings.length > 0 && Object.keys(mapped).length === 0) {
      return { success: false, message: `字段映射失败: ${warnings.join('; ')}` };
    }
  }

  const path = `/magicflu/service/s/jsonv2/${spaceId}/forms/${formId}/records`;
  const result = await apiRequest(config, 'POST', path, submitData);

  if (!result.success) {
    return { success: false, message: `创建记录失败: ${result.message}` };
  }

  const respData = result.data;
  if (respData?.errcode !== '0') {
    return {
      success: false,
      message: `创建记录失败: ${respData?.errmsg || '未知错误'}`,
      data: respData,
    };
  }

  return {
    success: true,
    message: `表单「${resolved.formLabel}」记录创建成功，ID: ${respData.id}`,
    data: respData,
    spaceLabel: resolved.spaceLabel,
    formLabel: resolved.formLabel,
  };
}

// ============ 修改记录 ============

export interface UpdateRecordParams {
  formHint: string;
  spaceHint?: string;
  recordId: string;
  data: Record<string, any>;
}

export async function updateRecordHandler(
  params: UpdateRecordParams,
  context: { config: Record<string, string> }
): Promise<MutationResult> {
  const config = buildConfig(context);

  if (!config.baseUrl) {
    return { success: false, message: '未配置 BASE_URL。' };
  }

  if (!params.data || Object.keys(params.data).length === 0) {
    return { success: false, message: '修改数据不能为空。' };
  }

  const resolved = await resolveSpaceForm(config, params.formHint, params.spaceHint);
  if (!resolved.success || !resolved.spaceId || !resolved.formId) {
    return { success: false, message: resolved.message };
  }

  const { spaceId, formId } = resolved;

  const fieldResult = await fetchFieldDefs(config, spaceId, formId);
  let submitData = params.data;
  if (fieldResult.success && fieldResult.fields.length > 0) {
    const { mapped, warnings } = mapDataKeys(fieldResult.fields, params.data);
    submitData = mapped;
    if (warnings.length > 0 && Object.keys(mapped).length === 0) {
      return { success: false, message: `字段映射失败: ${warnings.join('; ')}` };
    }
  }

  const path = `/magicflu/service/s/jsonv2/${spaceId}/forms/${formId}/records/entry/${params.recordId}`;
  const result = await apiRequest(config, 'PUT', path, submitData);

  if (!result.success) {
    return { success: false, message: `修改记录失败: ${result.message}` };
  }

  const respData = result.data;
  if (respData?.errcode !== '0') {
    return {
      success: false,
      message: `修改记录失败: ${respData?.errmsg || '未知错误'}`,
      data: respData,
    };
  }

  return {
    success: true,
    message: `表单「${resolved.formLabel}」记录修改成功。`,
    data: respData,
    spaceLabel: resolved.spaceLabel,
    formLabel: resolved.formLabel,
  };
}

// ============ 删除记录 ============

export interface DeleteRecordParams {
  formHint: string;
  spaceHint?: string;
  recordId: string;
}

export async function deleteRecordHandler(
  params: DeleteRecordParams,
  context: { config: Record<string, string> }
): Promise<MutationResult> {
  const config = buildConfig(context);

  if (!config.baseUrl) {
    return { success: false, message: '未配置 BASE_URL。' };
  }

  const resolved = await resolveSpaceForm(config, params.formHint, params.spaceHint);
  if (!resolved.success || !resolved.spaceId || !resolved.formId) {
    return { success: false, message: resolved.message };
  }

  const { spaceId, formId } = resolved;

  const path = `/magicflu/service/s/jsonv2/${spaceId}/forms/${formId}/records/entry/${params.recordId}`;
  const result = await apiRequest(config, 'DELETE', path);

  if (!result.success) {
    return { success: false, message: `删除记录失败: ${result.message}` };
  }

  const respData = result.data;
  if (respData?.errcode !== '0') {
    return {
      success: false,
      message: `删除记录失败: ${respData?.errmsg || '未知错误'}`,
      data: respData,
    };
  }

  return {
    success: true,
    message: `表单「${resolved.formLabel}」记录删除成功。`,
    data: respData,
    spaceLabel: resolved.spaceLabel,
    formLabel: resolved.formLabel,
  };
}
