import { http } from '@/utils/http/axios';

// [[ name ]] 接口（由低代码生成器生成）
const BASE_URL = '/api/[[ code ]]/';

// 分页/列表查询
export function get[[ camel ]]List(params) {
  return http.request({ url: BASE_URL, method: 'GET', params });
}

// 新增
export function add[[ camel ]](data) {
  return http.request({ url: BASE_URL, method: 'POST', data });
}

// 修改
export function update[[ camel ]](id, data) {
  return http.request({ url: `${BASE_URL}${id}/`, method: 'PUT', data });
}

// 删除
export function delete[[ camel ]](id) {
  return http.request({ url: `${BASE_URL}${id}/`, method: 'DELETE' });
}

// 按字典编码获取字典选项（label/value）
export async function getDictByCode(code) {
  const res = await http.request({ url: '/api/dictitem/by/code/', method: 'GET', params: { code } });
  return (res || []).map((item) => ({ label: item.label, value: item.value }));
}
