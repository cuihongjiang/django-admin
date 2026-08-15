<template>
  <div class="p-4">
    <n-card :bordered="false" class="mb-4 proCard">
      <div class="search-form">
        <n-form ref="searchFormRef" :model="searchParams" inline label-placement="left" label-width="auto" require-mark-placement="right-hidden">
[% for col in search_columns %]
          <n-form-item label="[[ col.title ]]">
            <n-input v-model:value="searchParams.[[ col.field ]]" placeholder="请输入[[ col.title ]]" clearable style="width: 180px" @keyup.enter="reloadTable" />
          </n-form-item>
[% endfor %]
          <n-form-item>
            <n-space>
              <n-button type="primary" :loading="loading" @click="reloadTable">
                <template #icon>
                  <n-icon><SearchOutlined /></n-icon>
                </template>
                查询
              </n-button>
              <n-button quaternary @click="resetSearch">
                <template #icon>
                  <n-icon><ReloadOutlined /></n-icon>
                </template>
                重置
              </n-button>
            </n-space>
          </n-form-item>
        </n-form>
      </div>
    </n-card>

    <n-card :bordered="false" class="proCard">
      <BasicTable
        :columns="columns"
        :request="loadDataTable"
        :row-key="(row) => row.id"
        :action-column="actionColumn"
        ref="actionRef"
      >
        <template #tableTitle>
          <n-space>
            <n-button type="primary" @click="handleAdd">
              <template #icon>
                <n-icon><PlusOutlined /></n-icon>
              </template>
              新增[[ name ]]
            </n-button>
          </n-space>
        </template>
      </BasicTable>
    </n-card>

    <n-modal v-model:show="showModal" :title="isEdit ? '编辑[[ name ]]' : '新增[[ name ]]'" preset="dialog" :style="{ width: '600px' }">
      <n-form ref="formRef" :model="formModel" :rules="formRules" label-placement="left" label-width="auto">
[% for f in form_fields %]
        <n-form-item label="[[ f.title ]]" path="[[ f.field ]]">
[% if f.component == 'select' %]
          <n-select v-model:value="formModel.[[ f.field ]]" :options="dictOptions['[[ f.dict_code ]]']" placeholder="请选择[[ f.title ]]" clearable />
[% elif f.component == 'date' %]
          <n-date-picker v-model:value="formModel.[[ f.field ]]" type="date" clearable class="w-full" />
[% elif f.component == 'switch' %]
          <n-switch v-model:value="formModel.[[ f.field ]]" />
[% elif f.component == 'textarea' %]
          <n-input v-model:value="formModel.[[ f.field ]]" type="textarea" placeholder="请输入[[ f.title ]]" />
[% else %]
          <n-input v-model:value="formModel.[[ f.field ]]" placeholder="请输入[[ f.title ]]" clearable />
[% endif %]
        </n-form-item>
[% endfor %]
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleSave">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
  import { h, reactive, ref, unref } from 'vue';
  import { useDialog, useMessage } from 'naive-ui';
  import { BasicTable, TableAction } from '@/components/Table';
  import { SearchOutlined, ReloadOutlined, PlusOutlined } from '@vicons/antd';
  import * as [[ camel ]]Api from './api';

  const dialog = useDialog();
  const message = useMessage();
  const actionRef = ref();
  const loading = ref(false);
  const saving = ref(false);
  const showModal = ref(false);
  const isEdit = ref(false);
  const formRef = ref();
  const currentId = ref(null);

  const searchParams = reactive({
[% for col in search_columns %]
    [[ col.field ]]: null,
[% endfor %]
  });

  const columns = [
[% for col in list_columns %]
    { title: '[[ col.title ]]', key: '[[ col.field ]]'[% if col.width %], width: [[ col.width ]][% endif %] },
[% endfor %]
  ];

  const actionColumn = reactive({
    width: 160,
    title: '操作',
    key: 'action',
    render(record) {
      return h(TableAction as any, {
        actions: [
          {
            label: '编辑',
            onClick: handleEdit.bind(null, record),
          },
          {
            label: '删除',
            onPositiveClick: () => handleDelete(record),
          },
        ],
      });
    },
  });

  const defaultForm = {
[% for f in form_fields %]
    [[ f.field ]]: null,
[% endfor %]
  };
  const formModel = reactive({ ...defaultForm });

  const formRules = {
[% for f in required_fields %]
    [[ f.field ]]: { required: true, message: '请输入[[ f.title ]]', trigger: ['blur', 'change'] },
[% endfor %]
  };

  // 数据字典选项：[[ dict_codes|join(', ') ]]
  const dictOptions = reactive({});
  async function loadDictOptions() {
[% for dc in dict_codes %]
    dictOptions['[[ dc ]]'] = await [[ camel ]]Api.getDictByCode('[[ dc ]]');
[% endfor %]
  }

  const loadDataTable = async (params) => {
    loading.value = true;
    try {
      return await [[ camel ]]Api.get[[ camel ]]List({ ...unref(searchParams), ...params });
    } finally {
      loading.value = false;
    }
  };

  function reloadTable() {
    actionRef.value?.reload();
  }

  function resetSearch() {
[% for col in search_columns %]
    searchParams.[[ col.field ]] = null;
[% endfor %]
    reloadTable();
  }

  function handleAdd() {
    isEdit.value = false;
    Object.assign(formModel, defaultForm);
    showModal.value = true;
  }

  function handleEdit(record) {
    isEdit.value = true;
    currentId.value = record.id;
    Object.assign(formModel, defaultForm, record);
    showModal.value = true;
  }

  function handleSave() {
    formRef.value?.validate(async (errors) => {
      if (errors) return;
      saving.value = true;
      try {
        if (isEdit.value) {
          await [[ camel ]]Api.update[[ camel ]](currentId.value, { ...formModel, id: currentId.value });
          message.success('修改成功');
        } else {
          await [[ camel ]]Api.add[[ camel ]]({ ...formModel });
          message.success('新增成功');
        }
        showModal.value = false;
        reloadTable();
      } finally {
        saving.value = false;
      }
    });
  }

  function handleDelete(record) {
    dialog.warning({
      title: '提示',
      content: `确定删除该记录吗？`,
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: async () => {
        await [[ camel ]]Api.delete[[ camel ]](record.id);
        message.success('删除成功');
        reloadTable();
      },
    });
  }

  loadDictOptions();
</script>
